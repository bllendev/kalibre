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
        self.username = "testuser"
        self.book = BookFactory.create()
        self.book_title = "some_book"
        self.json_links = "some_links"
