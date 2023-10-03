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

# localTrue, 200)
from books.tasks import send_book_email_task


CustomUser = get_user_model()


"""
docker compose exec web python manage.py test books.tests.test_tasks --parallel --noinput --failfast 
"""


class SendBookAjaxTaskTest(TestCase):
    def setUp(self):
        # mocks
        self.username = 'testuser'
        self.book_title = 'some_book'
        self.filetype = 'some_type'
        self.isbn = 'some_isbn'
        self.json_links = 'some_links'

    @patch('books.tasks.BookAPI')
    @patch('books.tasks.Email.get_email_dict')
    @patch('books.tasks.CustomUser.objects.get')
    def test_send_book_email_task(self, mock_get_user, mock_get_email_dict, mock_book_api):
        # act
        result = send_book_email_task(self.username, self.book_title, self.filetype, self.isbn, self.json_links)

        # assert
        self.assertTrue(mock_get_user.called)
        self.assertTrue(mock_get_email_dict.called)
        self.assertTrue(mock_book_api.called)
        self.assertEqual((True, 200), tuple(result))
