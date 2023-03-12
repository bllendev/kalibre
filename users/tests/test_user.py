from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from users.tests.factories import (
    CustomUserFactory,
)


class CustomUserTests(TestCase):

    def setUp(self):
        TEST_EMAIL_LIST = ["fake_@email.com", "fake_1@email.com"]
        self.test_user = CustomUserFactory().build()

        # email_list = list(self.email_addresses.all())
        # email_str = ""
        # if email_list:
        #     for email in email_list:
        #         email_str += f"{email}\n"
        # return email_str




        test_user_email_addres_str = self.test_user.email_address_str
        test_user_email_obj = self.test_user.email

        self.assertEqual(test_user_email_addres_str, self.test_user.email)


class SignupPageTests(TestCase):  # new
    username = "newuser"
    email = "newuser@email.com"

    def setUp(self):
        url = reverse("account_signup")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/signup.html")
        self.assertContains(self.response, "Sign Up")
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_signup_form(self):
        new_user = get_user_model().objects.create_user(self.username, self.email)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].username, self.username)
        self.assertEqual(get_user_model().objects.all()[0].email, self.email)