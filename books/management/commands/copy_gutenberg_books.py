import logging
from django.db import models
from django.core.management.base import BaseCommand
from books.models import Book, BookGutenberg

logger = logging.getLogger(__name__)


"""
docker compose exec web python manage.py copy_gutenberg_books
"""


class Command(BaseCommand):
    """
    Bulk populate the Book model from BookGutenberg records.
    ... book description exists
    ... subjects exists
    ... bookshelves exists

    Track records which don't have sufficient info
    to be collected in async celery job...
    """

    help = "Bulk populate the Book model from BookGutenberg records."

    def handle(self, *args, **options):
        """
        updates existing book records first
        creates new book records second
        """
        # create or update
        self.update_books()
        self.create_books()

        # log
        self.stdout.write("Done !")

    def update_books(self):
        books_to_update = []
        num_books_updated = 0
        index = 0
        # update existing records - prefetch !
        existing_gbooks = BookGutenberg.objects.filter(
            books__isnull=False
        ).prefetch_related(models.Prefetch("books", queryset=Book.objects.all()))
        for gutenberg_book in existing_gbooks.iterator(chunk_size=1000):
            index += 1

            # extract data
            # discern if any missing data...
            title = gutenberg_book.title
            description = gutenberg_book.description
            subjects = ", ".join(gutenberg_book.subjects)

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
                  Processed {index} records...
                """)

        # final update
        if books_to_update:
            Book.objects.bulk_update(
                books_to_update,
                ["title", "description", "subjects", "gutenberg"],
            )
            books_to_update = []

        self.stdout.write(f"Updated {num_books_updated} existing Books.")
        self.stdout.write("Book model population completed.")

    def create_books(self):
        # create new books
        books_to_create = []
        num_books_created = 0
        index = 0
        new_gbooks = BookGutenberg.objects.filter(books__isnull=True)
        for gutenberg_book in new_gbooks.iterator(chunk_size=1000):
            index += 1
            # extract data
            # discern if any missing data...
            title = gutenberg_book.title
            description = gutenberg_book.description
            bookshelves = ", ".join(gutenberg_book.bookshelves)
            subjects = ", ".join(gutenberg_book.subjects) + bookshelves

            # chunk by 1000
            if index % 1000 == 0:  # NOTE: debug will remove when working
                # bulk create new books
                if books_to_create:
                    Book.objects.bulk_create(books_to_create)
                    books_to_create = []
                    self.stdout.write(f"""
                          Processed {index} records...
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
