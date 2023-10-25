# django
import os
from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock

# factories
from books.tests.factories import BookFactory
from books.tests.constants import (
    TEST_QUERY,
    TEST_ISBN,
    TEST_BOOK_FILETYPE,
)

# local
from books.api.book_api import BookAPI
from books.api.api_book import APIBook
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

    @patch.object(BookAPI, "get_search_query_results", return_value=[APIBook(title=TEST_QUERY, isbn=TEST_ISBN, Mirror_1="file link")])
    def test_update_books(self, mock_get_search_query_results):
        book = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, author="test_author")  # NOTE: empty link should be updated

        # mock self.get_search_query_results() with different info\
        api = BookAPI(TEST_QUERY, force_api=True)
        api.update_books()

        book = Book.objects.get(pk=book.pk)
        self.assertIn("test_author", book.author)
        

    def test_get_book(self):
        TEST_BOOK = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, filetype=TEST_BOOK_FILETYPE)
        test_book = self.test_book_db.get_book(TEST_BOOK.isbn, TEST_BOOK.title, TEST_BOOK.filetype)
        self.assertEqual(test_book, TEST_BOOK)
