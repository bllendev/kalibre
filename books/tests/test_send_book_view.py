# from django.test import TestCase, Client
# from django.urls import reverse
# from books.tests.factories import BookFactory
# from users.models import CustomUser
# from users.tests.factories import (
#     EmailFactory,
# )
#
#
# """
# docker compose exec web python manage.py test books.tests.test_send_book_view --noinput --failfast
# TODO: make this test not run in cicd
# """
#
#
# class SendBookViewTests(TestCase):
#     TEST_EMAIL = "test@email.com"
#     TEST_USERNAME = "testuser"
#
#     def setUp(self):
#         self.client = Client()
#         self.test_email = EmailFactory.create(address=self.TEST_EMAIL)
#         self.test_user = CustomUser.objects.create_user(
#             username="testuser", password="12345"
#         )
#         self.test_user.email_addresses.add(self.test_email)
#         self.test_book = BookFactory(test_book=True)
#         self.url = reverse("send-book", args=[self.test_book.pk])
#
#     def test_send_book_authenticated_user(self):
#         # log the user in
#         self.client.login(username="testuser", password="12345")
#
#         mirror_1 = "http://library.lol/main/CDD0C7BB84700F371E6F4675947D7456"
#
#         # send POST request with book data
#         response = self.client.post(self.url, {"mirror_1": mirror_1})
#
#         # check response and database state
#         self.assertEqual(response.status_code, 200)
#         self.test_user.refresh_from_db()
#         self.assertIn(self.test_book, self.test_user.my_books.all())
#
#     def test_send_book_unauthenticated_user(self):
#         # send POST request without logging the user in
#         response = self.client.post(self.url, {"book": {}})
#
#         # check that the response is a redirect to the login page
#         self.assertEqual(response.status_code, 302)
#         self.assertIn(reverse("account_login"), response["Location"])
#
#     def test_send_book_book_does_not_exist(self):
#         # log the user in
#         self.client.login(username="testuser", password="12345")
#
#         # use a nonexistent book pk
#         invalid_url = reverse("send-book", args=[9999])
#
#         # use valid book data
#         book_data = {
#             "ID": "123",
#             "Author": "Test Author",
#             "Title": "Test Title",
#         }
#
#         # send POST request
#         response = self.client.post(invalid_url, {"book": book_data})
#
#         # check response for server error
#         self.assertEqual(response.status_code, 500)
#
#     def test_send_book_without_book_data(self):
#         # log the user in
#         self.client.login(username="testuser", password="12345")
#
#         # send POST request without book data
#         response = self.client.post(self.url)
#
#         # assert error due to missing data
#         self.assertEqual(response.status_code, 500)
