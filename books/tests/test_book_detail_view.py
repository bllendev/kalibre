from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import Http404

from books.models import Book
from users.tests.factories import CustomUserFactory
from books.factory import BookFactory


"""
docker compose exec web python manage.py test books.tests.test_book_detail_view --failfast
"""


class BookDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(BookDetailViewTestCase, cls).setUpClass()
        cls.user = CustomUserFactory(username="testuser", password="12345")
        cls.credentials = {"username": "testuser", "password": "12345"}
        cls.book = BookFactory()

    def setUp(self):
        logged_in = self.client.login(**self.credentials)
        self.assertTrue(logged_in)

    def test_book_detail_view_get(self):
        response = self.client.get(reverse("book-detail", args=[self.book.pk]))
        book = response.context["book"]
        book_obj = Book.objects.get(pk=book.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn("book", response.context)
        self.assertEqual(str(book_obj.id), self.book.id)

    def test_book_detail_view_not_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(reverse("book-detail", args=[self.book.pk]))
        self.assertRedirects(response, f"/accounts/login/?next=/books/{self.book.pk}")

    # def test_book_detail_with_nonexistent_book_raises_404(self):
    #     with self.assertRaises(Http404):
    #         # fake book pk
    #         pk = self.book.pk
    #         self.book.delete()
    #         self.client.get(reverse("book-detail", args=[pk]))
