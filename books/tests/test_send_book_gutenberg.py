from django.test import TestCase, Client
from django.urls import reverse
from books.factory import BookFactory
from users.models import CustomUser
from users.tests.factories import EmailFactory


"""
docker compose exec web python manage.py test books.tests.test_send_book_gutenberg
"""


# TODO: make this test safe for cicd
# class SendBookGutenbergViewTests(TestCase):
#     TEST_EMAIL = "test@gmail.com"
#     TEST_USERNAME = "testuser"
#     TEST_PASSWORD = "12345"
#
#     def setUp(self):
#         self.client = Client()
#         self.test_email = EmailFactory.create(address=self.TEST_EMAIL)
#         self.test_user = CustomUser.objects.create_user(
#             username=self.TEST_USERNAME, password=self.TEST_PASSWORD
#         )
#         self.test_user.email_addresses.add(self.test_email)
#         self.test_book = BookFactory(test_book=True)
#         self.url = reverse("send-book-gutenberg", args=[self.test_book.pk])
#
#     def test_send_book_authenticated_user(self):
#         self.client.login(username=self.TEST_USERNAME, password=self.TEST_PASSWORD)
#         link = "https://www.gutenberg.org/ebooks/10000.kindle.images"
#         response = self.client.post(self.url, {"link": link})
#
#         # assert
#         self.assertEqual(response.status_code, 200)
#         self.test_user.refresh_from_db()
#         book_ids = [str(b.id) for b in self.test_user.my_books.all()]
#         self.assertIn(str(self.test_book.id), book_ids)
#
# def test_send_book_unauthenticated_user(self):
#     response = self.client.post(self.url, {"link": "http://gutenberg.org/12345"})
#
#     # assert
#     self.assertEqual(response.status_code, 302)
#     login_url = reverse("account_login")
#     self.assertIn(login_url, response["Location"])
#     self.assertIn(f"next={self.url}", response["Location"])
#
# def test_send_book_book_does_not_exist(self):
#     self.client.login(username=self.TEST_USERNAME, password=self.TEST_PASSWORD)
#     invalid_url = reverse("send-book-gutenberg", args=[9999])
#     response = self.client.post(invalid_url, {"link": "http://gutenberg.org/12345"})
#     self.assertEqual(response.status_code, 500)
#
# def test_send_book_without_link_data(self):
#     self.client.login(username=self.TEST_USERNAME, password=self.TEST_PASSWORD)
#     response = self.client.post(self.url)
#     self.assertEqual(response.status_code, 500)
