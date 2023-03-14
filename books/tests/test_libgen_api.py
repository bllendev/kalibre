from django.test import TestCase
from django.conf import settings

import os
import pickle

from users.tests.factories import CustomUserFactory
from books.tests.factories import BookFactory
from books.libgen_api import LibgenSearch, SearchRequest
from books.utils import LibgenAPI, LibgenBook

import json

"""
    - HOW TO RUN TESTS:
    - ... $ docker compose exec web python manage.py test --noinput --parallel
"""

TEST_QUERY = "harry potter"

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
    #     test_pickle_path = os.path.join(settings.BASE_DIR, "books", "tests", "pkl", "test_hp_book.pkl")
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

    def setUp(self):
        self.test_user = CustomUserFactory.build()
        self.libgen_db = LibgenAPI(TEST_QUERY, force_api=False)
        self.libgen_api = LibgenAPI(TEST_QUERY, force_api=True)

    def test_book_db_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        TEST_CREATED_BOOK = BookFactory.create(title=TEST_QUERY)
        test_books = self.libgen_db._book_db_search()
        test_book_ids = [book.id for book in test_books if book.id == TEST_CREATED_BOOK.id]
        self.assertTrue(test_book_ids)

    def test_get_api_book_choices(self):
        pass
        # titles = self.libgen.search_title(self.search_query)
        # authors = self.libgen.search_author(self.search_query)
        # _book_list = titles + authors

    def test_get_book_list(self):
        pass
        # # check books in db first
        # books = self._book_db_search()

        # # if not reasonable selection, do fresh query using libgen api
        # if not books or self.force_api:
        #     db_books_by_id = {book.isbn: book for book in books}    
        #     api_books_by_id = {book.isbn: book.__dict__ for book in self._get_book_list()}
        #     created_books_by_id = {}

        #     # filter books by what is already in our db (if any)
        #     for isbn, new_book_dict in api_books_by_id.items():
        #         if isbn not in db_books_by_id:
        #             book_obj = Book(**new_book_dict)
        #             created_books_by_id[isbn] = book_obj

        #     # save filtered books
        #     books = {book for isbn, book in created_books_by_id.items()}
        #     bulk_save(books)

        # return books

    def test_get_book_file_path_from_links(self):
        pass
        # from django.conf import settings
        # import requests

        # # get book record from db!
        # new_book = Book.objects.filter(isbn=isbn).first()          # THESE ISBN SHOULD BE ALL UNIQUE RIGHT ??? @AG++
        # if not new_book:
        #     new_book = Book.objects.filter(title__icontains=book_title, filetype=filetype).first()

        # # write file to path (will use file to send - then we will delete file)
        # new_file_path = os.path.join(settings.BASE_DIR, f"{new_book.title}.{new_book.filetype}")

        # # get book file content
        # i = 0
        # temp_book_file_dl = None
        # while not temp_book_file_dl:
        #     temp_book_file_link = new_book.get_book_download_content(links[i])
        #     temp_book_file_dl = requests.get(temp_book_file_link)

        # # write book file content
        # with temp_book_file_dl and open(new_file_path, "wb") as f:
        #     f.write(temp_book_file_dl.content)
        #     f.close()

    def test_send_book_file(self):
        pass
        # """emails actual book file to recipient addresses"""
        # from django.core import mail

        # # get book file path (safety bypass if no path)
        # book_file_path = self.get_book_file_path_from_links(links, book_title, filetype, isbn)        # web scraper
        # if book_file_path is None:
        #     return

        # # send book as email to recipients
        # with mail.get_connection() as connection:
        #     recipient_emails = [email.address for email in user.email_addresses.all()]
        #     template_message = copy.deepcopy(self.EMAIL_TEMPLATE_LIST)                        # NOTE: deep copy
        #     template_message[3] = recipient_emails

        #     email_message = mail.EmailMessage(*tuple(template_message), connection=connection)
        #     email_message.attach_file(book_file_path)
        #     email_message.send(fail_silently=False)

        # # delete book_file after sending!
        # os_silent_remove(book_file_path)
