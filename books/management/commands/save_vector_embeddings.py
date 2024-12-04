import logging
from django.core.management.base import BaseCommand
from django.db.models import Q

from books.models import Book
from books.tasks import books_save_vector

logger = logging.getLogger(__name__)


"""
docker compose exec web python manage.py save_vector_embeddings --missing-data
"""


class Command(BaseCommand):
    help = "Process Books and save vector embeddings with optional filters."

    def add_arguments(self, parser):
        # filter only records without vector embeddings yet
        parser.add_argument(
            "--missing-data",
            action="store_true",
            help="Only process books with missing data attributes.",
        )
        # potential filter flag for author, title, etc.
        parser.add_argument(
            "--title-contains",
            type=str,
            help="Filter books whose title contains the given string.",
        )

        # additional filter for specific authors
        parser.add_argument(
            "--author", type=str, help="Filter books by a specific author name."
        )

    def handle(self, *args, **options):
        query = Q()

        # apply optional filters depending on command line flags
        if options["missing_data"]:
            query &= Q(vector_search__isnull=True)

        if options["title_contains"]:
            query &= Q(title__icontains=options["title_contains"])

        if options["author"]:
            query &= Q(authors__name__icontains=options["author"])

        # fetch eligible books according to built query
        eligible_books = Book.objects.filter(query)
        book_ids = eligible_books.values_list("id", flat=True)
        if not book_ids:
            self.stdout.write("No books found for the given criteria.")
            return

        self.stdout.write(f"Found {len(book_ids)} books for processing.")

        # batch process
        chunk_size = 200
        for i in range(0, len(book_ids), chunk_size):
            batch = book_ids[i: i + chunk_size]
            self.stdout.write(
                f"{chunk_size} Vector processing tasks have been dispatched."
            )
            books_save_vector.delay(batch)

        self.stdout.write("All Vector processing tasks have been dispatched.")
