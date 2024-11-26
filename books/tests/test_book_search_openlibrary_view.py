from django.test import TestCase, Client
from django.urls import reverse

from books.tests.constants import TEST_QUERY
from books.models import Book
from books.api._api_openlibrary import OpenLibraryAPI

"""
docker compose exec web python manage.py test books.tests.test_book_search_openlibrary_view --failfast
"""


class BookSearchOpenlibraryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("book-search-openlibrary")

    def test_books_are_created(self):
        # ensure no books exists!
        Book.objects.all().delete()

        # call the actual view via client
        response = self.client.post(self.url, {"query": "sample query"})

        # check for success responses
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Book.objects.all().exists())
        created_book = Book.objects.all().first()
