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
from books.api._api_openlibrary import OpenLibraryAPI
from books.api._api_libgen import LibgenAPI
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

        # openlibrary apibook
        cls.openlibrary_book = {
            "key": "12345",
            "author_name": "test_author",  # author_key for id
            "title": "test_title",
            "cover_i": "test_cover_url",
        }

        # libgen apibook
        cls.libgen_book = {
            "ID": "12345",
            "Author": "test_author",
            "Title": "test_title",
            "Extension": "epub",
        }
    
    @patch.object(OpenLibraryAPI, "get_book_search_results")
    @patch.object(LibgenAPI, "get_book_search_results")
    def test_get_search_query_results(self, mock_libgen_api, mock_openlibrary_api):
        # mock
        mock_libgen_api.return_value = [self.libgen_book]
        mock_openlibrary_api.return_value = [self.openlibrary_book]

        # act
        books = BookAPI().get_search_query_results()

        # assert
        self.assertTrue(books, "bad books!")
        self.assertEquals(len(books), 1)
        mock_libgen_api.called_once()
        mock_openlibrary_api.called_once()

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
        test_book = BookAPI().get_book(TEST_BOOK.isbn, TEST_BOOK.title, TEST_BOOK.filetype)
        self.assertEqual(test_book, TEST_BOOK)
