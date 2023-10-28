from django.db.models import Case, When
from django.db import models
import json

# local
from books.models import Book
from books.api.api_book import APIBook, find_matching_books
from books.api._api_openlibrary import OpenLibraryAPI
from books.api._api_libgen import LibgenAPI

# logging
import logging

logger = logging.getLogger(__name__)


class BookAPI:
    """
    - Handles all Book API calls, normalizing books from different sources
      and removing potential duplicates.
    - Also handles the creation of new books and pulling from the database.
    """

    def __init__(self, search_query=None, force_api=False):
        self.force_api = force_api
        self.search_query = search_query
        self.openlibrary_api = OpenLibraryAPI()
        self.libgen_api = LibgenAPI()

    def fetch_books_from_api(self, api):
        try:
            return [APIBook(**book) for book in api.get_book_search_results(self.search_query)]
        except TypeError as e:
            logger.error(f"Error fetching books from {api.__class__.__name__}: {e}")
            return list()

    def get_search_query_results(self):
        openlibrary_book_set = self.fetch_books_from_api(self.openlibrary_api)
        libgen_book_set = self.fetch_books_from_api(self.libgen_api)

        # get final output
        output_list = list()
        for book in openlibrary_book_set:
            epub_match = find_matching_books(book, libgen_book_set, "epub")
            if epub_match:
                book.json_links = epub_match.json_links
                book.filetype = epub_match.filetype
            output_list.append(book)

        if not output_list:
            raise TypeError(f"openlibrary_book_set: {openlibrary_book_set} | libgen_book_set: {libgen_book_set}")

        return set(output_list)

    def update_books(self):
        try:
            db_books = Book.search(self.search_query)
            if len(db_books) < 3 or self.force_api:
                for api_book in self.get_search_query_results():
                    Book.objects.update_or_create(isbn=vars(api_book)['isbn'], defaults=vars(api_book))
        except AttributeError as e:
            logger.error(f"{e} | self.search_query: {self.search_query}")
            raise e

    def get_unique_book_list(self):
        self.update_books()
        return Book.search(self.search_query).order_by("-filetype", "-cover_url")

    def get_book(self, isbn, book_title, filetype):
        return (
            Book.objects.filter(isbn__icontains=isbn, filetype=filetype).first() or
            Book.objects.filter(title__icontains=book_title, filetype=filetype).first()
        )
