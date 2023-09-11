from __future__ import absolute_import, unicode_literals

from django.http import JsonResponse
from books._api import BookAPI
from django.contrib.auth import get_user_model
from users.models import Email


from celery import shared_task


CustomUser = get_user_model()


@shared_task
def send_book_ajax_task(request):
    """
    ajax celery task to send single ebook to user email addresses
    - uses books.models.Book.ssn
    """
    import json

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax and request.method == 'POST':
        # organize post data
        post_dict = {key: val for key, val in request.POST.items() if "book" in key}
        post_dict_keys = list(post_dict.keys())

        # extract book info
        # print(f"post_dict_keys: {post_dict_keys}")   # handy debug
        json_links = json.loads(post_dict[post_dict_keys[0]])
        book_title, filetype, isbn = post_dict_keys[0].split("__")
        book_title = book_title.replace("book_", "")
        filetype = filetype.replace("type_", "")
        isbn = isbn.replace("isbn_", "")

        # extract user info
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        emails = user.email_addresses.all()

        # extract emails
        email_dict = Email.get_email_dict(emails)

        # get API book and send
        book_api = BookAPI()
        book = book_api.get_book(isbn, book_title, filetype)

        for lang, emails in email_dict.items():
            book.send(emails=emails, language=lang)

        return JsonResponse({'status': True}, status=200)

    return JsonResponse({'status': False}, status=400)
