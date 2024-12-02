import logging
from django.db import models
from django.core.management.base import BaseCommand
from books.models import Book, BookGutenberg
from books.tasks import books_save_vector

logger = logging.getLogger(__name__)


"""
docker compose exec web python manage.py copy_gutenberg_books
docker compose exec web python manage.py copy_gutenberg_books --save_vector
"""


class Command(BaseCommand):
    """
    Bulk populate the Book model from BookGutenberg records.
    - also builds vector embeddings upfront iff...
    ... book description exists
    ... subjects exists
    ... bookshelves exists

    Track records which don't have sufficient info
    to be collected in async celery job...
    """

    help = "Bulk populate the Book model from BookGutenberg records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--save_vector",
            action="store_true",
            help="Flag to save vector embeddings after processing.",
        )

    def handle(self, *args, **options):
        # prepare lists for bulk operations
        books_to_create = []
        num_books_created = 0
        books_to_update = []
        num_books_updated = 0
        books_with_missing_data = []

        index = 0

        # update existing records - prefetch !
        existing_gbooks = BookGutenberg.objects.filter(
            books__isnull=False
        ).prefetch_related(models.Prefetch("books", queryset=Book.objects.all()))
        for gutenberg_book in existing_gbooks.iterator(chunk_size=1000):
            index += 1
            title = gutenberg_book.title
            description = gutenberg_book.description
            bookshelves = ", ".join(gutenberg_book.bookshelves)
            subjects = ", ".join(gutenberg_book.subjects)

            # discern if any missing data...
            # ... to be populated via openlibrary api
            all_keys_exist = all([title, description, bookshelves, subjects])
            if not all_keys_exist:
                books_with_missing_data.append(gutenberg_book)

            # NOTE: bookshelves discont. in 2020, but may have good info
            subjects = bookshelves + subjects

            # case: update
            # get fk to existing book record
            book = gutenberg_book.books.first()
            book.title = title
            book.description = description
            book.subjects = subjects
            books_to_update.append(book)
            num_books_updated += 1

            # chunk by 1000
            if index % 1000 == 0:  # NOTE: debug will remove when working
                # bulk update existing books
                if books_to_update:
                    Book.objects.bulk_update(
                        books_to_update,
                        ["title", "description", "subjects", "gutenberg"],
                    )
                    books_to_update = []

                self.stdout.write(f"""
                  Processed {index}/{existing_gbooks.count()} records...
                """)
                break

        # final update
        if books_to_update:
            Book.objects.bulk_update(
                books_to_update,
                ["title", "description", "subjects", "gutenberg"],
            )
            books_to_update = []

        self.stdout.write(f"Updated {num_books_updated} existing Books.")

        # create new books
        index = 0
        new_gbooks = BookGutenberg.objects.filter(books__isnull=True)
        for gutenberg_book in new_gbooks.iterator(chunk_size=1000):
            index += 1
            title = gutenberg_book.title
            description = gutenberg_book.description
            bookshelves = ", ".join(gutenberg_book.bookshelves)
            subjects = ", ".join(gutenberg_book.subjects)

            # chunk by 1000
            if index % 1000 == 0:  # NOTE: debug will remove when working
                # bulk create new books
                if books_to_create:
                    Book.objects.bulk_create(books_to_create)
                    books_to_create = []

                    self.stdout.write(f"""
                          Processed {index}/{new_gbooks.count()} records...
                        """)

            # case: create (bulk)
            b = Book(
                title=title,
                description=description,
                subjects=subjects,
                gutenberg=gutenberg_book,
            )
            books_to_create.append(b)
            num_books_created += 1

        # final bulk create
        if books_to_create:
            Book.objects.bulk_create(books_to_create)
            books_to_create = []

        # logs
        self.stdout.write(f"Created {num_books_created} Books.")
        self.stdout.write("Book model population completed.")

        # save vector embeddings ?
        if options["save_vector"]:
            self.stdout.write("saving vector embeddings !")

            book_ids = []
            i = 0
            for b in Book.objects.filter(gutenberg__isnull=False).iterator(
                chunk_size=1000
            ):
                # increment
                i += 1

                # book ids append, save chunk
                book_ids.append(str(b.id))
                if i % 1000 == 0:
                    books_save_vector.delay(book_ids)
                    book_ids = []

            # last set of book_ids
            if book_ids:
                books_save_vector.delay(book_ids)
                book_ids = []

        self.stdout.write("Done !")
