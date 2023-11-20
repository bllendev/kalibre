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
        # mocks
        self.username = 'testuser'
        self.book = BookFactory.create()
        self.book_title = 'some_book'
        self.filetype = 'some_type'
        self.isbn = 'some_isbn'
        self.json_links = 'some_links'

    @patch('books.tasks.CustomUser.objects.get')
    @patch('books.models.Book.send', return_value=(True, 200))
    def test_send_book_email_task(self, mock_book_send, mock_get_user):
        mock_user = CustomUserFactory.create(username=self.username)
        mock_get_user.return_value = mock_user
        mock_user.get_email_dict = MagicMock(return_value={"es": "test@email.com"})

        # act
        result = send_book_email_task(self.username, self.book)

        # assert
        mock_get_user.assert_called_once_with(username=self.username)
        mock_user.get_email_dict.assert_called_once()
        mock_book_send.assert_called_once()
        self.assertEqual((True, 200), tuple(result))
