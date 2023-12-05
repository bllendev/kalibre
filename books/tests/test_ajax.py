from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json
from unittest.mock import Mock, patch

from users.tests.factories import (
    CustomUserFactory,
    EmailFactory,
)
from books.tests.factories import BookFactory

from users.models import Email
from books.ajax import toggle_translate_email, send_book_ajax, add_email


"""
docker compose exec web python manage.py test books.tests.test_ajax --noinput --parallel --failfast
"""

CustomUser = get_user_model()


class SendBookAjaxTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.book = BookFactory.create(title='Test Book')
        self.url = reverse('send_book_ajax', args=[self.book.pk])
        self.login_url = f"{reverse('account_login')}?next={self.url}"

    def test_send_book_ajax_authenticated_user_post_request(self):
        self.client.login(username='testuser', password='12345')
        with patch('books.tasks.send_book_email_task', return_value=(True, 200)) as mock_task:
            response = self.client.post(self.url)
            self.assertTrue(mock_task.called)
            self.assertEqual(response.status_code, 200)

    def test_send_book_ajax_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, self.login_url, status_code=302, target_status_code=200)

    def test_send_book_ajax_non_post_request(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 500)

    # def test_send_book_ajax_book_not_found(self):
    #     self.client.login(username='testuser', password='12345')
    #     url = reverse('send_book_ajax', args=[999])  # Non-existent book ID
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 500)

    def test_send_book_ajax_user_not_found(self):
        # Create request with non-existent user
        response = self.client.post(self.url, **{'REMOTE_USER': 'nonexistentuser'})
        self.assertRedirects(response, self.login_url, status_code=302, target_status_code=200)

    def test_send_book_ajax_general_exception(self):
        self.client.login(username='testuser', password='12345')
        with patch('books.tasks.send_book_email_task', side_effect=Exception('Test error')):
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, 500)


class TestBookAjax(TestCase):
    """Test Case for Ajax methods used in Book sub-app
    """

    def setUp(self):
        self.test_email = EmailFactory.create()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        self.user.email_addresses.add(self.test_email)
        self.user.save()
        self.book = BookFactory.create()
        self.factory = RequestFactory()

    def test_add_email_ajax(self):
        url = reverse('add_email')
        request = self.factory.post(url, {'email_input': 'test@example.com'}, HTTP_HX_RESPONSE_FORMAT='mobile')
        request.user = self.user
        
        # Mock the request_is_ajax_bln to always return True
        with patch('books.ajax.request_is_ajax_bln', return_value=True):
            response = add_email(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Email.objects.filter(address='test@example.com').exists())
        self.assertIn('text/html', response['Content-Type'])

    def test_add_email_non_ajax(self):
        url = reverse('add_email')
        request = self.factory.post(url, {'email_input': 'test@example.com'})
        request.user = self.user
        
        # No mocking needed here as we are testing non-AJAX functionality
        response = add_email(request)

        # Expecting a redirect to 'my_profile', so status code should be 302
        self.assertTrue(response)
        self.assertTrue(Email.objects.filter(address='test@example.com').exists())

    def test_send_book_ajax(self):
        pass

    # def test_toggle_translate_email_bad_post_request(self):
    #     url = reverse("toggle_translate_email", kwargs={"pk": self.test_email.pk})
    #     client = Client()
    #     login_success = self.client.login(username=self.user.username, password="testpassword")
    #     self.assertTrue(login_success)

    #     # create a POST request
    #     response = client.post(url)

    #     # check that it returns a 404 status code
    #     self.assertEqual(response.status_code, 400)

    #     # create POST with no headers.get('X-Requested-With') == 'XMLHttpRequest'
    #     data = {
    #         "translate_email_pk[]": self.test_email.pk,
    #         "language_selection": "es"
    #     }
    #     response = self.client.post(url, data)  # NOT AJAX SHOULD FAIL

    #     self.assertEqual(response.status_code, 400)

    # def test_toggle_translate_email_post_request(self):
    #     url = reverse("toggle_translate_email", kwargs={"pk": self.test_email.pk})
    #     client = Client()
    #     login_success = self.client.login(username=self.user.username, password="testpassword")
    #     self.assertTrue(login_success)

    #     data = {
    #         "translate_email_pk[]": self.test_email.pk,
    #         "language_selection": "es"
    #     }
    #     response = self.client.post(url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

    #     # assert response
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsInstance(response, JsonResponse)
    #     self.assertEqual(response.json(), {'status': True, 'translate_email_pk': str(self.test_email.pk)})

    #     # assert changes
    #     self.test_email.refresh_from_db()
    #     self.assertEquals(self.test_email.translate_file, "es")

    # @patch('books.ajax.request_is_ajax_bln', return_value=True)
    # @patch('books.tasks.send_book_email_task', return_value=(True, 200))
    # @patch('books.api.book_api.BookAPI')
    # @patch('books.ajax.CustomUser.objects.get')
    # def test_send_book_ajax(self, mock_get_custom_user, MockBookAPI, mock_send_book_email_task, mock_ajax_check):
    #     # mock user
    #     mock_get_custom_user.return_value = self.user

    #     # create a mock book object for BookAPI().get_book() to return
    #     MockBookAPI.return_value.get_book.return_value = self.book

    #     # create a POST request
    #     data = {
    #         'book_title__type_pdf__isbn_12345': '{"link": "http://example.com/book.pdf"}'
    #     }
    #     request = self.factory.post('/books/send_book_ajax/', data)
    #     request.user = self.user

    #     # call view
    #     response = send_book_ajax(request)
    #     response_data = json.loads(response.content)

    #     # assert response is as expected
    #     self.assertIsInstance(response, JsonResponse)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response_data['status'], True)

    #     # assert book was added to the user's books (if needed)
    #     self.assertIn(self.book, self.user.my_books.all())
