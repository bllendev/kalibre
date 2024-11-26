from django.test import TestCase
from books.api._api_libgen import (
    LibgenAPI,
)
from books.tests.constants import (
    TEST_QUERY,
    TEST_QUERY_AUTHOR,
    TEST_AUTHOR_KEY,
)
from authors.factory.author import AuthorFactory
from books.tests.factories import BookFactory

from books.models import Book


"""
docker compose exec web python manage.py test books.tests.test_api_libgen --noinput --failfast
"""


class TestLibgenAPI(TestCase):
    def setUp(self):
        self.api = LibgenAPI()
        self.api_response = {
            "title": "My Sweet-orange Tree",
            "isbn": [
                "964913980X",
                "9789649139807",
                "1782692452",
                "1536203289",
                "9781782692454",
                "9781536203288",
            ],
            "key": "/works/OL286593W",
            "cover_i": "10413035",
            "publish_date": ["2019", "Mar 16, 2011"],
            "subject": ["Brazil, fiction", "Children's fiction"],
            "author_key": ["OL2643489A"],
            "author_name": ["Jose Mauro De Vasconcelos"],
        }


# TODO: add skip if in cicd so we don't spam api
# def test_fetch_books(self):
#     books = self.api.fetch_books(TEST_QUERY)
#     self.assertTrue(books)
