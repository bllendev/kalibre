from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
import json
from unittest.mock import Mock, patch

from books.tests.factories import BookFactory
from users.tests.factories import (
    EmailFactory,
)

from users.models import Email
from users.ajax import toggle_translate_email, add_email


CustomUser = get_user_model()


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
        request = self.factory.post(url, {'email_input': 'test@example.com'})
        request.user = self.user
        
        # Mock the request_is_ajax_bln to always return True
        with patch('books.ajax.request_is_ajax_bln', return_value=True):
            response = add_email(request)

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