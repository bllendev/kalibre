from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.tests.factories import CustomUserFactory
from books.factory import BookFactory, BookGutenbergFactory


"""
docker compose exec web python manage.py test books.tests.test_get_gutenberg_links_view
"""


class GetGutenbergLinksViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(GetGutenbergLinksViewTestCase, cls).setUpClass()
        cls.user = CustomUserFactory(username="testuser", password="12345")
        cls.credentials = {"username": "testuser", "password": "12345"}
        cls.book = BookFactory(title="Sample Book")
        cls.gutenberg_book = BookGutenbergFactory(title="Sample Book")

    def setUp(self):
        logged_in = self.client.login(**self.credentials)
        self.assertTrue(logged_in)

    def test_get_gutenberg_links_view_get(self):
        url = reverse("get-gutenberg-links", args=[self.book.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("book", response.context)
        self.assertIn("gutenberg_books", response.context)
        self.assertEqual(str(response.context["book"].id), str(self.book.id))

    def test_get_gutenberg_links_view_not_logged_in_redirects(self):
        self.client.logout()
        url = reverse("get-gutenberg-links", args=[self.book.pk])
        response = self.client.get(url)
        login_url = "/accounts/login/"
        next_url = f"?next=/books/get-gutenberg-links/{self.book.pk}/"
        self.assertRedirects(response, f"{login_url}{next_url}")
