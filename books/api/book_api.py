# django
from django.db.models import Case, When
from django.db import models
import json

# local
from books.models import Book
from books.api.api_book import APIBook

import logging

logger = logging.getLogger(__name__)


class BookAPI:
    """
    - handles all Book API calls, normalizing books from different sources
    and removing potential duplicates.
    - also handles the creation of new books and pulling from the database
    """

    def __init__(self, search_query=None, force_api=False):
        self.force_api = force_api
        self.search_query = search_query

        # self.gutenberg_api = GutenbergAPI(search_query)
    
    def get_search_query_results(self):
        api = APIBook()
        return api(self.search_query)

    def update_books(self):
        try:
            db_books = Book.search(self.search_query)
            if len(db_books) < 3 or self.force_api:
                # get API results
                api_books = self.get_search_query_results()

                # Update or create books using API data
                for api_book in api_books:
                    # Convert APIBook attributes into a dictionary
                    book_data = vars(api_book)
                    
                    # Update or create based on ISBN
                    Book.objects.update_or_create(isbn=book_data['isbn'], defaults=book_data)
        except AttributeError as e:
            logger.error(f"{e} api_books: {api_books} | db_books: {db_books} | self.search_query: {self.search_query}")
            raise e

    def get_unique_book_list(self):
        # update books
        self.update_books()

        # TODO: consider implementing embeddings
        # Book.objects.create_and_embed_books(**book_info)

        return Book.search(self.search_query).order_by("-filetype")  # fresh query after updating

    def get_book(self, isbn, book_title, filetype):
        """
        gets the intended book from the database
        """
        new_book = Book.objects.filter(isbn__icontains=isbn, filetype=filetype).first()  # THESE ISBN SHOULD BE ALL UNIQUE RIGHT ??? @AG++
        if not new_book:
            new_book = Book.objects.filter(title__icontains=book_title, filetype=filetype).first()
        return new_book
