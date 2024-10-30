import unittest
from unittest.mock import patch, Mock
from books.api._api_openlibrary import OpenLibraryAPI


"""
docker compose exec web python manage.py test books.tests.test_api_openlibrary --parallel --noinput --failfast
"""


class TestOpenLibraryAPI(unittest.TestCase):
    """
    """

    def setUp(self):
        self.api = OpenLibraryAPI()
