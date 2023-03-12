from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from users.tests.factories import (
    CustomUserFactory,
    EmailFactory,
)


class CustomUserTests(TestCase):
    TEST_EMAIL_LIST = ["fake_@email.com", "fake_1@email.com"]
    TEST_OUTPUT = "\n".join(TEST_EMAIL_LIST)

    def setUp(self):
        self.test_user = CustomUserFactory().build()

    def test_email_address_str(self):
        self.assertEqual(self.test_user.email_address_str, self.TEST_OUTPUT)


class SignupPageTests(TestCase):

    TEST_EMAIL = "testuser@email.com"
    TEST_USERNAME = "testuser"

    def setUp(self):
        self.test_email = EmailFactory.build(address=self.TEST_EMAIL)
        self.test_user = CustomUserFactory.build(username=self.TEST_USER_DICT, email=self.TEST_EMAIL)

        url = reverse("account_signup")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/signup.html")
        self.assertContains(self.response, "Sign Up")
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")
