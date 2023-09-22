# django
from django.test import TestCase, RequestFactory, Client
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import importlib

# factories
from users.tests.factories import CustomUserFactory, EmailFactory
from books.tests.factories import BookFactory

# local
from books.tasks import send_book_email_task


CustomUser = get_user_model()


"""
docker compose exec web python manage.py test books.tests.test_tasks --parallel --noinput --failfast 
"""


class SendBookAjaxTaskTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.test_email = EmailFactory.create()
        self.test_user = CustomUserFactory()
        self.test_user.email_addresses.add(self.test_email)
        self.test_user.save()
        self.test_user.refresh_from_db()
        self.book = BookFactory.create()

        # mocks
        self.username = 'testuser'
        self.book_title = 'some_book'
        self.filetype = 'some_type'
        self.isbn = 'some_isbn'
        self.json_links = 'some_links'

    @patch('books.tasks.BookAPI')  # replace with the actual import
    @patch('books.tasks.Email.get_email_dict')  # replace with the actual import
    @patch('books.tasks.CustomUser.objects.get')  # replace with the actual import
    def test_send_book_email_task(self, mock_get_user, mock_get_email_dict, mock_book_api):
        mock_book = MagicMock()

        result = send_book_email_task(self.username, self.book_title, self.filetype, self.isbn, self.json_links)

        self.assertTrue(mock_get_user.called)
        self.assertTrue(mock_get_email_dict.called)
        self.assertTrue(mock_book_api.called)
        self.assertEqual(result, {'status': True})
