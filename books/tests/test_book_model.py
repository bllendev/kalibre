# django
from django.conf import settings
from django.test import TestCase

# tools
import os
import pickle

# local
from users.tests.factories import CustomUserFactory
from books.tests.factories import BookFactory
from books.tests.constants import TEST_QUERY


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

    def test_book_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        test_books = self.test_book.search(query=TEST_QUERY)
        test_book_ids = [book.id for book in test_books if book.id == self.test_book.id]
        self.assertTrue(test_book_ids)
        self.assertIn(self.test_book.id, test_book_ids, "test_book was not found in db search results")
