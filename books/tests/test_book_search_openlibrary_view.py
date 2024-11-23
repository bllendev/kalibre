from django.test import TestCase, Client
from django.urls import reverse

from books.tests.constants import TEST_QUERY
from books.models import Book


"""
docker compose exec web python manage.py test books.tests.test_book_search_openlibrary_view --failfast
"""


class BookSearchOpenlibraryViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    # NOTE: test was working, need to block api ping duringtest... TODO...
    # def test_books_are_created(self):
    #     # send a POST request to your view
    #     breakpoint()
    #     url = reverse("book-search-openlibrary")
    #     response = self.client.post(url, {"query": TEST_QUERY})
    #
    #     # assuming it returns 200 on success
    #     self.assertEqual(response.status_code, 200)
    #
    #     # verifying the books count in the database
    #     self.assertTrue(Book.objects.all().exists())
