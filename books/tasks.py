from __future__ import absolute_import, unicode_literals

from django.http import JsonResponse
from books._api import BookAPI
from django.contrib.auth import get_user_model
from users.models import Email


from celery import shared_task


CustomUser = get_user_model()


@shared_task
def send_book_ajax_task(request):
    import json

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax and request.method == 'POST':
        # organize post data
        post_dict = {key: val for key, val in request.POST.items() if "book" in key}
        post_dict_keys = list(post_dict.keys())

        # extract book info
        json_links = json.loads(post_dict[post_dict_keys[0]])
        book_title, filetype, isbn = post_dict_keys[0].split("__")
        book_title = book_title.replace("book_", "")
        filetype = filetype.replace("type_", "")
        isbn = isbn.replace("isbn_", "")

        # extract user info
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        emails = user.email_addresses.all()

        # group emails
        email_group_dict = {
            "en":  emails.filter(translate_file=""),
            Email.TRANSLATE_EN_ES: emails.filter(translate_file=Email.TRANSLATE_EN_ES),
        }

        # get libgenbook
        book_api = BookAPI()
        for lang, email_group in email_group_dict.items():
            book = None
            if email_group:  # NOTE: if no emails, don't send book
                book = book_api.get_book(isbn, book_title, filetype)
                if book:  # NOTE: only send book if real
                    email_group = [email.address for email in email_group]
                    book.send(email_list=email_group, language=lang)

        return JsonResponse({'status': True}, status=200)

    return JsonResponse({'status': False}, status=400)