# django
from django.test import TestCase
from django.conf import settings

# local
from users.tests.factories import CustomUserFactory
from books.tests.factories import BookFactory
from books.libgen_api import LibgenSearch, SearchRequest
from books.libgen_api import LibgenAPI, LibgenBook
from books.models import Book

# tools
import os
import json
import pickle

"""
    - HOW TO RUN TESTS:
    - ... $ docker compose exec web python manage.py test --noinput --parallel
"""

TEST_QUERY = "my sweet orange tree"

TEST_ISBN = "2670677"       # my sweet orange tree

TEST_BOOK_FILETYPE = "epub"

TEST_COLUMNS = [
    "ID",
    "Author",
    "Title",
    "Publisher",
    "Year",
    "Pages",
    "Language",
    "Size",
    "Extension",
    "Mirror_1",
    "Mirror_2",
    "Mirror_3",
    "Mirror_4",
    "Mirror_5",
    "Edit",
]

TEST_LIBGEN_MIRRORS = [
    "https://libgen.is",
    "http://libgen.gs",
    "http://gen.lib.rus.ec",
    "http://libgen.rs",
    "https://libgen.st",
    "https://libgen.li",
]

TEST_EMAIL_TEMPLATE_LIST = [
    '',                                         # empty subject line
    '',                                         # empty message line
    str(settings.DEFAULT_FROM_EMAIL),           # from email
    list(),                                     # recipient_list
]

TEST_STABLE_FILE_TYPES = {"epub", "mobi"}


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


class TestLibgenAPI(TestCase):

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    @classmethod
    def setUpClass(cls):
        super(TestLibgenAPI, cls).setUpClass()

        # create libgen api instances (one for db search, one for api search)
        cls.test_libgen_db = LibgenAPI(TEST_QUERY, force_api=False)
        cls.test_libgen_api = LibgenAPI(TEST_QUERY, force_api=True)

    def test_book_db_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        TEST_BOOK = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, filetype=TEST_BOOK_FILETYPE)
        test_books = self.test_libgen_db._book_db_search()
        test_book_ids = [book.id for book in test_books if book.id == TEST_BOOK.id]
        self.assertTrue(test_book_ids)

    def test_get_libgen_book_list(self):
        api_book_choices = self.test_libgen_api._get_libgen_book_list()
        api_book_choices_ids = [book.isbn for book in api_book_choices if book.isbn == TEST_ISBN]
        self.assertTrue(api_book_choices_ids)

    def test_get_unique_book_list(self):
        test_libgen = LibgenAPI(TEST_QUERY, force_api=False)

        # case 0: no books in db -- > books in api
        Book.objects.all().delete()     # clear books
        test_books = test_libgen.get_unique_book_list()
        test_book = [book.isbn for book in test_books if book.isbn == TEST_ISBN]
        self.assertTrue(test_book)

        # assert get_unique_book_list saved books to db
        test_book_exists = Book.objects.filter(isbn=TEST_ISBN).exists()
        self.assertTrue(test_book_exists)

        # case 1: books in db
        Book.objects.all().delete()     # clear books
        TEST_BOOK = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, filetype=TEST_BOOK_FILETYPE)
        test_books_db = test_libgen.get_unique_book_list()        # should refer to books in db if they exist
        test_books = [book.isbn for book in test_books_db if book.isbn == TEST_ISBN]
        self.assertTrue(test_books)

        # case 2: books in db, force_api=True
        test_libgen_api = LibgenAPI(TEST_QUERY, force_api=True)
        test_books_api = test_libgen_api.get_unique_book_list()
        test_books = [book.isbn for book in test_books_api if book.isbn == TEST_ISBN]
        self.assertTrue(test_books)

    def test_get_book(self):
        TEST_BOOK = BookFactory.create(title=TEST_QUERY, isbn=TEST_ISBN, filetype=TEST_BOOK_FILETYPE)
        test_book = self.test_libgen_db.get_book(TEST_BOOK.isbn, TEST_BOOK.title, TEST_BOOK.filetype)
        self.assertEqual(test_book, TEST_BOOK)
