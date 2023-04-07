from __future__ import absolute_import, unicode_literals

from django.http import JsonResponse
from books.libgen_api import LibgenAPI
from django.contrib.auth import get_user_model
from users.models import Email


from celery import shared_task


CustomUser = get_user_model()


@shared_task
def send_book_ajax_task(request):
    import json

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax and request.method == 'POST':
        # organize
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
        libgen = LibgenAPI()
        for lang, email_group in email_group_dict.items():

            book = None
            if email_group:
                book = libgen.get_book(isbn, book_title, filetype)
                print(f"book found!!! {book}")

            # send book if real
            if book and email_group:
                email_group = [email.address for email in email_group]
                book.send(email_list=email_group, language=lang)

        return JsonResponse({'status': True}, status=200)

    return JsonResponse({'status': False}, status=400)