# django
from django.test import TestCase, RequestFactory, Client
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse

# factories
from users.tests.factories import CustomUserFactory, EmailFactory
from books.tests.factories import BookFactory

# local
from books.tasks import send_book_ajax_task


CustomUser = get_user_model()


"""
docker compose exec web python manage.py test books.tests.test_tasks --parallel --noinput --failfast 
"""


class SendBookAjaxTaskTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.test_email = EmailFactory.create()
        self.test_user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.test_user.email_addresses.add(self.test_email)
        self.test_user.save()
        self.book = BookFactory.create()

    @patch('books.tasks.BookAPI')
    def test_send_book_ajax_task_fail(self, mock_bookapi):
        # Setup
        mock_bookapi_instance = mock_bookapi.return_value
        mock_bookapi_instance.get_book.return_value = None

        request = self.factory.post('/fake-url/', {
            'book_test_title__type_pdf__isbn_1234567890': '{"fake": "data"}',
        })
        request.user = self.test_user

        # call the task
        response = send_book_ajax_task(request)

        # Check the response
        self.assertEqual(response.status_code, 400)

    @patch('books._api.Book.send')
    def test_send_book_ajax_task(self, mock_book_send):
        url = reverse("send_book_ajax")
        client = Client()
        login_success = client.login(username=self.test_user.username, password="testpassword")
        self.assertTrue(login_success)

        data = {self.book.ssn: "fake_data"}
        response = self.client.post(url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        self.assertTrue(isinstance(response, JsonResponse))
        self.assertTrue(self.response.status_code == 200)
        mock_book_send.assert_called()
