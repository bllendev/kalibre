# django
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# tools
import json

# local
from ai.models import Conversation
from ai.ajax import query_ai, set_latest_messages


"""
docker compose exec web python manage.py test ai.tests --parallel --noinput --failfast
"""

CustomUser = get_user_model()


class AIAjaxTest(TestCase):
    """
    Tests for the ajax calls used for the AI Librarian
    """

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.test_user = CustomUser.objects.create_user(username='testuser', password='default_password')

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

    def test_create_conversation(self):
        self.client = Client()
        self.client.login(username=self.test_user.username, password="default_password")

        response = self.client.post(reverse('create_conversation'), 
                            content_type='application/x-www-form-urlencoded')

        self.assertEqual(response.status_code, 200)
        self.assertTrue('conversation_id' in response.json())
