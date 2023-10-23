# django
from django.test import TestCase, RequestFactory, Client
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from django.urls import reverse
import json
import importlib

# factories
from users.tests.factories import CustomUserFactory, EmailFactory
from books.tests.factories import BookFactory


import unittest
from unittest.mock import patch, Mock
from books.utils import send_emails


"""
docker compose exec web python manage.py test --noinput --failfast
"""

# TODO: write tests for send_emails
# class TestSendEmails(unittest.TestCase):
    
#     # @patch('books.utils.mail.get_connection')
#     # @patch('books.utils.mail.EmailMessage')
#     # @patch('books.utils.os_silent_remove')
#     # def test_send_emails_success(self, mock_remove, mock_email, mock_connection):
#     #     email = 'test@example.com'
#     #     template_message = "Some template message"
#     #     file_paths = ['file1.txt', 'file2.txt']
        
#     #     # Mock successful email sending
    #     mock_email_instance = mock_email.return_value
    #     mock_email_instance.send.return_value = None

    #     result = send_emails(template_message, file_paths)
    #     self.assertTrue(result)

    #     # Assert that os_silent_remove is called for each file
    #     mock_remove.assert_any_call('file1.txt')
    #     mock_remove.assert_any_call('file2.txt')

    # @patch('books.utils.mail.get_connection')
    # @patch('books.utils.mail.EmailMessage')
    # @patch('books.utils.os_silent_remove')
    # def test_send_emails_failure(self, mock_remove, mock_email, mock_connection):
    #     email = 'test@example.com'
    #     template_message = "Some template message"
    #     file_paths = ['file1.txt', 'file2.txt']

    #     # Mock failure in email sending
    #     mock_email_instance = mock_email.return_value
    #     mock_email_instance.send.side_effect = Exception("Some error")

    #     with self.assertRaises(Exception):
    #         send_emails(email, template_message, file_paths)

    #     # Even in the event of a failure, files should be removed
    #     mock_remove.assert_any_call('file1.txt')
    #     mock_remove.assert_any_call('file2.txt')
