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
        self.test_email = EmailFactory.create(address=self.TEST_EMAIL_LIST[0])
        self.test_email_1 = EmailFactory.create(address=self.TEST_EMAIL_LIST[1])
        self.test_user = CustomUserFactory.create(username="testuser")
        self.test_user.email_addresses.add(self.test_email, self.test_email_1)
        self.test_user.save()

    def test_email_address_str(self):
        self.assertEqual(self.test_user.email_addresses_str, self.TEST_OUTPUT)


class SignupPageTests(TestCase):

    TEST_EMAIL = "testuser@email.com"
    TEST_USERNAME = "testuser"

    def setUp(self):
        self.test_email = EmailFactory.create(address=self.TEST_EMAIL)
        self.test_user = CustomUserFactory.create(username=self.TEST_USERNAME)
        self.test_user.email_addresses.add(self.test_email)
        self.test_user.save()

        url = reverse("account_signup")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/signup.html")
        self.assertContains(self.response, "Sign Up")