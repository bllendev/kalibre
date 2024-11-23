from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.tests.factories import CustomUserFactory


"""
docker compose exec web python manage.py test books.tests.test_views --failfast
"""


class SearchResultsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SearchResultsViewTestCase, cls).setUpClass()
        cls.user = CustomUserFactory(username="testuser", password="12345")
        cls.credentials = {"username": "testuser", "password": "12345"}

    def setUp(self):
        logged_in = self.client.login(**self.credentials)
        self.assertTrue(logged_in)

    def test_search_view_get(self):
        # Note how 'somebook' is passed as an argument inside reverse
        response = self.client.get(
            reverse("search-results", args=["somebook"]))
        self.assertEqual(response.status_code, 200)

        # Check if the query is correctly shown in the response context
        self.assertIn("query", response.context)
        self.assertEqual(response.context["query"], "somebook")

    def test_search_view_post_with_found_books(self):
        response = self.client.get(
            reverse("search-results", args=["somebook"]))
        self.assertEqual(response.status_code, 200)
