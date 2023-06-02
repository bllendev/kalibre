# django
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# tools
import json
from unittest.mock import patch

# local
from ai.models import TokenUsage, Conversation, Message
from ai.ajax import update_token_usage, query_ai, set_latest_messages, ai_librarian

# factories
from users.tests.factories import (
    CustomUserFactory,
    EmailFactory,
)


"""
docker compose exec web python manage.py test ai.tests --parallel --noinput --failfast
"""

CustomUser = get_user_model()


class AIAjaxTest(TestCase):
    """
    Tests for the ajax calls used for the AI Librarian
    """

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.test_user = CustomUser.objects.create_user(username='testuser', password='default_password')

    # def test_update_token_usage(self):
    #     # Create an instance of a GET request.
    #     request = self.factory.get('/some-url')

    #     # Recall that middleware are not supported. You can simulate a
    #     # logged-in user by setting request.user manually.
    #     request.user = self.test_user

    #     update_token_usage(request, [{"content": "test message"}])
    #     self.assertEqual(TokenUsage.objects.count(), 1)

    def test_set_latest_messages(self):
        messages = set_latest_messages([
            {"role": "system", "content": "Hello, who are you?"},
            {"role": "user", "content": "I'm a test."},
            {"role": "system", "content": "Nice to meet you, test."}
        ])
        self.assertEqual(len(messages), 2)

    def test_query_ai(self):
        # Simulate a logged-in user by setting request.user manually.
        request = self.factory.post('/some-url')
        request.user = self.test_user
        request.POST._mutable = True
        request.POST['conversation_id'] = Conversation.objects.create(user=request.user).id
        request.POST._mutable = False

        ai_response = query_ai(request, "Hello, who are you?")
        self.assertIsNotNone(ai_response)

    def test_ai_librarian(self):
        self.client = Client()

        # JSON dumps the messages
        with patch('ai.ajax.query_ai') as mocked_query_ai:
            # Set the return value of the mock
            mocked_query_ai.return_value = 'Hello, I am an AI.'

            # Login the test user using the test client
            self.client.login(username=self.test_user.username, password="default_password")

            response = self.client.post(reverse('ai_librarian'), 
                                data={"user_message": json.dumps("Hello, who are you?")},
                                content_type='application/x-www-form-urlencoded')

            # Make sure the mock was called
            mocked_query_ai.assert_called_once()

        self.assertEqual(response.status_code, 200)

    def test_create_conversation(self):
        self.client = Client()
        self.client.login(username=self.test_user.username, password="default_password")

        response = self.client.post(reverse('create_conversation'), 
                            content_type='application/x-www-form-urlencoded')

        self.assertEqual(response.status_code, 200)
        self.assertTrue('conversation_id' in response.json())