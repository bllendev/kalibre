from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from users.tests.factories import (
    CustomUserFactory,
    EmailFactory,
)
from books.tests.factories import BookFactory

from books.ajax import toggle_translate_email


"""
docker compose exec web python manage.py test books.tests.test_ajax --noinput --parallel --failfast
"""

CustomUser = get_user_model()


class TestBookAjax(TestCase):
    """Test Case for Ajax methods used in Book sub-app
    """

    def setUp(self):
        self.test_email = EmailFactory.create()
        self.test_user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.test_user.email_addresses.add(self.test_email)
        self.test_user.save()
        self.book = BookFactory.build()
        self.factory = RequestFactory()

    def test_toggle_translate_email_bad_post_request(self):
        url = reverse("toggle_translate_email")
        client = Client()
        login_success = self.client.login(username=self.test_user.username, password="testpassword")
        self.assertTrue(login_success)

        # create a GET request
        response = client.get(url)

        # check that it returns a 404 status code
        self.assertEqual(response.status_code, 400)

        # create POST with no headers.get('X-Requested-With') == 'XMLHttpRequest'
        data = {
            "translate_email_pk[]": self.test_email.pk,
            "language_selection": "es"
        }
        response = self.client.post(url, data)  # NOT AJAX SHOULD FAIL

        self.assertEqual(response.status_code, 400)

    def test_toggle_translate_email_post_request(self):
        url = reverse("toggle_translate_email")
        client = Client()
        login_success = self.client.login(username=self.test_user.username, password="testpassword")
        self.assertTrue(login_success)

        data = {
            "translate_email_pk[]": self.test_email.pk,
            "language_selection": "es"
        }
        response = self.client.post(url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        # assert response
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.json(), {'status': True, 'translate_email_pk': str(self.test_email.pk)})

        # assert changes
        self.test_email.refresh_from_db()
        self.assertEquals(self.test_email.translate_file, "es")
