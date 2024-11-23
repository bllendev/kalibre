# django
from django.conf import settings
from django.test import TestCase

# tools
import os
import pickle
import json

# factories
from users.tests.factories import CustomUserFactory
from books.tests.factories import BookFactory
from books.tests.constants import TEST_QUERY

# local
from books.models import Book

TEST_BOOK_PKL_PATH = os.path.join(
    settings.BASE_DIR, "books", "tests", "_test_book.pkl")

TEST_EMBEDDINGS_PATH = os.path.join(
    settings.BASE_DIR, "books", "tests", "_test_query_embeddings.json"
)

"""
docker compose exec web python manage.py test books.tests.test_book_model --noinput
"""


class BookTest(TestCase):
    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    @classmethod
    def setUpClass(cls):
        super(BookTest, cls).setUpClass()

        # open book pkl
        with open(TEST_BOOK_PKL_PATH, "rb") as f:
            cls.test_epub = pickle.load(f)

        # open saved embeddings for user book search
        with open(TEST_EMBEDDINGS_PATH, "rb") as f:
            cls.test_embeddings = json.load(f)

        # create test user
        cls.test_user = CustomUserFactory.create()

        # create test book
        cls.test_book = BookFactory.create(
            test_book=True)  # orange tree book :)
        # cls.test_book.save(
        #     save_vector=True
        # )  # NOTE: explicit save vector to set embeddings
        cls.test_book.refresh_from_db()

    def test_save_vector(self):
        """vector gets saved via def save()"""
        test_book = BookFactory(vector_search=None)
        test_book.save(save_vector=True)
        test_book.refresh_from_db()
        self.assertTrue(test_book.vector_search)

    def test_book_pkl(self):
        self.assertTrue(self.test_epub)

    def test_search(self):
        """checks db first (bypass api query if record exists)"""
        # NOTE: test_embeddings associated with TEST_QUERY
        test_books = Book.search(
            query=TEST_QUERY, embeddings=self.test_embeddings)
        self.assertTrue(test_books)
        self.assertEqual(
            self.test_book,
            test_books.first(),
            "test_book was not found in db search results",
        )
