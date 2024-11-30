# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth import get_user_model
#
# from books.factory import BookFactory
# """
# docker compose exec web python manage.py test books.tests.test_ajax --noinput --parallel --failfast
# """
#
# CustomUser = get_user_model()
#
#
# class SendBookAjaxTest(TestCase):
#
#     def setUp(self):
#         self.client = Client()
#         self.user = CustomUser.objects.create_user(username='testuser', password='12345')
#         self.book = BookFactory.create(title='Test Book')
#         self.url = reverse('send_book_ajax', args=[self.book.pk])
#         self.login_url = f"{reverse('account_login')}?next={self.url}"
#
#     def test_send_book_ajax_unauthenticated_user(self):
#         response = self.client.get(self.url)
#         self.assertRedirects(response, self.login_url, status_code=302, target_status_code=200)
#
#     def test_send_book_ajax_non_post_request(self):
#         self.client.login(username='testuser', password='12345')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 500)
#
#     # def test_send_book_ajax_book_not_found(self):
#     #     self.client.login(username='testuser', password='12345')
#     #     url = reverse('send_book_ajax', args=[999])  # Non-existent book ID
#     #     response = self.client.post(url)
#     #     self.assertEqual(response.status_code, 500)
#
#     def test_send_book_ajax_user_not_found(self):
#         # Create request with non-existent user
#         response = self.client.post(self.url, **{'REMOTE_USER': 'nonexistentuser'})
#         self.assertRedirects(response, self.login_url, status_code=302, target_status_code=200)
