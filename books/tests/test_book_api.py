# django
import os
from django.test import TestCase
from unittest.mock import Mock

# factories
from books.tests.factories import BookFactory
from books.tests.constants import (
    TEST_QUERY,
    TEST_ISBN,
    TEST_BOOK_FILETYPE,
)

# local
from books.api.book_api import BookAPI
from books.models import Book


"""
docker compose exec web python manage.py test books.tests.test_book_api --noinput --parallel
"""


class TestBookAPI(TestCase):

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    @classmethod
    def setUpClass(cls):
        super(TestBookAPI, cls).setUpClass()

        # create book api instances (one for db search, one for api search)
        cls.test_book_db = BookAPI(TEST_QUERY, force_api=False)
        cls.test_book_api = BookAPI(TEST_QUERY, force_api=True)

    def test_book_db_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        TEST_BOOK = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, filetype=TEST_BOOK_FILETYPE)
        test_books = self.test_book_db._book_db_search()
        test_book_ids = [book.id for book in test_books if book.id == TEST_BOOK.id]
        self.assertTrue(test_book_ids)

    def test_get_unique_book_list(self):
        test_book_api = BookAPI(TEST_QUERY, force_api=False)

        # case 0: no books in db -- > books in api
        Book.objects.all().delete()     # clear books
        test_books = test_book_api.get_unique_book_list()
        test_book = [book.isbn for book in test_books if book.isbn == TEST_ISBN]
        self.assertTrue(test_book)

        # assert get_unique_book_list saved books to db
        test_book_exists = Book.objects.filter(isbn=TEST_ISBN).exists()
        self.assertTrue(test_book_exists)

        # case 1: books in db
        Book.objects.all().delete()     # clear books
        TEST_BOOK = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, filetype=TEST_BOOK_FILETYPE)
        test_books_db = test_book_api.get_unique_book_list()        # should refer to books in db if they exist
        test_books = [book.isbn for book in test_books_db if book.isbn == TEST_ISBN]
        self.assertTrue(test_books)

        # case 2: books in db, force_api=True
        test_book_api = BookAPI(TEST_QUERY, force_api=True)
        test_books_api = test_book_api.get_unique_book_list()
        test_books = [book.isbn for book in test_books_api if book.isbn == TEST_ISBN]
        self.assertTrue(test_books)

    def test_get_book(self):
        TEST_BOOK = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, filetype=TEST_BOOK_FILETYPE)
        test_book = self.test_book_db.get_book(TEST_BOOK.isbn, TEST_BOOK.title, TEST_BOOK.filetype)
        self.assertEqual(test_book, TEST_BOOK)
