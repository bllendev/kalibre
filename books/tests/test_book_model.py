# django
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock

# local
from users.tests.factories import CustomUserFactory
from books.tests.factories import BookFactory
from books.libgen_api import LibgenSearch, SearchRequest
from books.libgen_api import LibgenAPI, LibgenBook
from books.models import Book
from books.tests.test_libgen_api import (
    TEST_QUERY,
    TEST_ISBN,
    TEST_BOOK_FILETYPE,
)

# tools
import os
import json
import pickle


TEST_BOOK_PKL_PATH = os.path.join(settings.BASE_DIR, 'books', 'tests', '_test_book.pkl')


class BookTest(TestCase):

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    @classmethod
    def setUpClass(cls):
        super(BookTest, cls).setUpClass()

        # # open and assert test book
        # with open(TEST_BOOK_PKL_PATH, "rb") as f:
        #     cls.test_epub = pickle.load(f)

        # create test user
        cls.test_user = CustomUserFactory.create()

        # create test book
        cls.test_book = BookFactory.create(
            title="My Sweet Little Orange Tree",
            author="De Vasconcelos, José Mauro;Entrekin, Alison",
            filetype=TEST_BOOK_FILETYPE,
            isbn=TEST_ISBN,
            json_links='[\"http://library.lol/main/CDD0C7BB84700F371E6F4675947D7456\", \"http://libgen.lc/ads.php?md5=CDD0C7BB84700F371E6F4675947D7456\", \"https://library.bz/main/edit/CDD0C7BB84700F371E6F4675947D7456\"]'
        )

    # def test_book_pkl(self):
    #     self.assertTrue(self.test_epub)

    def test_book_ssn(self):
        self.assertEqual(self.test_book.ssn, 'book_My Sweet Little Orange Tree__type_epub__isbn_2670677')

    def test_book_get_absolute_url(self):
        url = reverse('book_detail', args=[str(self.test_book.id)])
        self.assertEqual(self.test_book.get_absolute_url(), url)

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