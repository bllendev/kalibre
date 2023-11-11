# django
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock

# tools
import os
import pickle

# local
from users.tests.factories import CustomUserFactory
from books.tests.factories import BookFactory
from books.models import Book
from books.tests.test_api_libgen import (
    TEST_QUERY,
    TEST_ISBN,
    TEST_BOOK_FILETYPE,
)


TEST_BOOK_PKL_PATH = os.path.join(settings.BASE_DIR, 'books', 'tests', '_test_book.pkl')


class BookTest(TestCase):

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    @classmethod
    def setUpClass(cls):
        super(BookTest, cls).setUpClass()

        # open and assert test book
        with open(TEST_BOOK_PKL_PATH, "rb") as f:
            cls.test_epub = pickle.load(f)

        # create test user
        cls.test_user = CustomUserFactory.create()

        # create test book
        cls.test_book = BookFactory.create(test_book=True)   # orange tree book :)

    def test_book_pkl(self):
        self.assertTrue(self.test_epub)

    def test_book_ssn(self):
        self.assertEqual(self.test_book.ssn, 'book_My Sweet Little Orange Tree__type_epub__isbn_2670677')

    def test_book_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        test_books = self.test_book.search(query=TEST_QUERY)
        test_book_ids = [book.id for book in test_books if book.id == self.test_book.id]
        self.assertTrue(test_book_ids)
        self.assertIn(self.test_book.id, test_book_ids, "test_book was not found in db search results")

    @patch("requests.get")
    def test_book_create_book_file(self, mock_requests_get):
        # Set up the mock requests.get() response
        mock_response = MagicMock()
        mock_response.content = b"Book file content"
        mock_requests_get.return_value = mock_response

        # Call the _create_book_file() method and check the output
        book_file_path = "/tmp/book.epub"
        self.test_book._create_book_file(book_file_path, language="en")
        with open(book_file_path, "rb") as f:
            self.assertEqual(f.read(), b"Book file content")

    @patch.object(Book, "_set_cover_url", return_value="test_cover_url")
    @patch.object(Book, "_set_cover", return_value=MagicMock())
    def test_get_cover_url(self, mock_set_cover, mock_set_cover_url):
        # case 0: cover does not exist - cover_url does not exist
        # should set cover_url and recall get_cover_url to set cover as intended
        with self.subTest("case 0: cover does not exist - cover_url does not exist"):
            self.test_book.cover_url = ""
            self.test_book.cover = None
            self.test_book.save()

            # act
            cover_url = self.test_book.get_cover_url()

            # assert
            mock_set_cover.assert_called_once()
            mock_set_cover_url.assert_called_once()
        
        # reset mocks for next subtest
        mock_set_cover.reset_mock()
        mock_set_cover_url.reset_mock()

        # case 1: cover does not exist - cover_url exists
        with self.subTest("case 1: cover does not exist - cover_url exists"):
            self.test_book.cover_url = "existing_cover_url"
            self.test_book.cover = None

            # act
            cover_url = self.test_book.get_cover_url()

            # assert
            mock_set_cover.assert_called_once()
            mock_set_cover_url.assert_not_called()
        
        # reset mocks for next subtest
        mock_set_cover.reset_mock()
        mock_set_cover_url.reset_mock()

        # case 2: cover exists
        with self.subTest("case 2: cover exists"):
            mock_cover = MagicMock()
            mock_cover.url = "existing_cover_url_with_cover"
            self.test_book.cover = mock_cover
            self.test_book.cover_url = "existing_cover_url_with_cover"

            # act
            cover_url = self.test_book.get_cover_url()

            # assert
            mock_set_cover.assert_not_called()
            mock_set_cover_url.assert_not_called()

        # case 3: error occurs, gracefully fall back on stock image
        with self.subTest("case 3: error occurs, gracefully fall back on stock image"):
            self.test_book.cover = None
            self.test_book.cover_url = ""

            # induce an error by making _set_cover raise an exception
            mock_set_cover.side_effect = Exception("induced error")

            # act
            cover_url = self.test_book.get_cover_url()

            # assert
            self.assertEqual(cover_url, "/static/books/generic_book_cover.jpg")

    # def test_convert_book_file(self):  # NOTE: does actual call to kalibre-ebook-convert microservice
    #     TEST_FILE = os.path.join(settings.BASE_DIR, "requirements.txt")
    #     book_file_path = self.test_book._convert_book_file(TEST_FILE, "pdf")
    #     self.assertTrue(book_file_path)

    # @patch("books.models.Book._get_book_download_content")
    # def test_book_get_book_file_path_from_links(self, mock_get_book_download_content):
    #     # Set up the mock _get_book_download_content() response
    #     mock_get_book_download_content.return_value = "https://example.com/book.epub"

    #     # Call the get_book_file_path_from_links() method and check the output
    #     book_file_path = self.test_book.get_book_file_path_from_links(language="en")
    #     self.assertEqual(book_file_path, "/tmp/My Sweet Little Orange Tree.epub")

    # @patch("books.models.Book.get_book_file_path_from_links")
    # @patch("django.core.mail.EmailMessage.send")
    # def test_book_send(self, mock_email_send, mock_get_book_file_path_from_links):
    #     # Set up the mock get_book_file_path_from_links() response
    #     mock_get_book_file_path_from_links.return_value = "/tmp/book.epub"

    #      # Call the send() method and check the output
    #     self.test_book.send(email_list=["test@example.com"], language="en")
    #     self.assertTrue(mock_email_send.called)
