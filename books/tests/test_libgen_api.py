# django
import os
import json
import pickle
from django.test import TestCase, RequestFactory
from django.conf import settings
from unittest.mock import patch, Mock

# factories
from users.tests.factories import CustomUserFactory, EmailFactory
from books.tests.factories import BookFactory
from books.tests.constants import (
    TEST_QUERY,
    TEST_ISBN,
    TEST_BOOK_FILETYPE,
    TEST_COLUMNS,
    TEST_LIBGEN_MIRRORS,
    TEST_EMAIL_TEMPLATE_LIST,
    TEST_STABLE_FILE_TYPES,
)

# local
from books.tasks import send_book_email_task
from users.models import Email
from books.api_libgen import LibgenSearch, SearchRequest
from books.api_libgen import LibgenAPI
from books.models import Book


"""
    - HOW TO RUN TESTS:
    - ... $ docker compose exec web python manage.py test --noinput --parallel
"""


class TestLibgenSearch(TestCase):

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    def setUp(self):
        self.libgen_search = LibgenSearch()
        self.libgen_book = None

    #     # open the file for reading in binary mode
    #     test_pickle_path = os.path.join(settings.BASE_DIR, "books", "tests", "test_hp_book.pkl")
    #     with open(test_pickle_path) as test_pickle:
    #         # unpickle the list object from the file
    #         self.test_results = pickle.load(test_pickle)

    # def test_search_title(self):
    #     results = self.libgen_search.search_title(TEST_QUERY)
    #     self.assertTrue(results)
    #     self.assertEquals(results, self.test_results)

    # def test_search_author(self):
    #     results = self.libgen_search.search_author(TEST_QUERY)
    #     self.assertTrue(results)

    # def test_resolve_download_links(self):
    #     results = self.libgen_search.resolve_download_links(self.libgen_book)
    #     self.assertTrue(results)


class TestSearchRequest(TestCase):
    """
        - USAGE: req = search_request.SearchRequest("[QUERY]", search_type="[title]")
    """

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    def setUp(self):
        self.test_search_request = SearchRequest("harry potter")

    def test_constants(self):
        self.assertEqual(self.test_search_request.COLUMNS, TEST_COLUMNS)
        self.assertEqual(self.test_search_request.LIBGEN_MIRRORS, TEST_LIBGEN_MIRRORS)

    def test_strip_i_tag_from_soup(self):
        pass

    def test_get_search_url(self):
        pass

    def test_get_search_page(self):
        pass

    def test_aggregate_request_data(self):
        pass


# class TestLibgenAPI(TestCase):
"""NOTE: not testing api in ci/cd pipeline
"""

#     _multiprocess_can_split_ = True
#     _multiprocess_shared_ = False

#     @classmethod
#     def setUpClass(cls):
#         super(TestLibgenAPI, cls).setUpClass()

#         # create libgen api instances (one for db search, one for api search)
#         cls.test_libgen_api = LibgenAPI(TEST_QUERY)

#     def test_get_libgen_book_list(self):
#         api_book_choices = self.test_libgen_api._get_libgen_book_list()
#         api_book_choices_ids = [book["ID"] for book in api_book_choices if book["ID"] == TEST_ISBN]
#         self.assertTrue(api_book_choices_ids)

#     def test_get_unique_book_list(self):
#         test_libgen = LibgenAPI(TEST_QUERY)
#         Book.objects.all().delete()     # clear books
#         test_books = test_libgen.get_unique_book_list()
#         test_book = [book["ID"] for book in test_books if book["ID"] == TEST_ISBN]
#         self.assertTrue(test_book)
