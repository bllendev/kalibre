from __future__ import absolute_import, unicode_literals

from django.http import JsonResponse
from books._api import BookAPI
from django.contrib.auth import get_user_model
from users.models import Email


from celery import shared_task


CustomUser = get_user_model()


@shared_task
def send_book_email_task(username, book_title, filetype, isbn, json_links):
    """celery task to send books to associated emails
    """
    try:
        user = CustomUser.objects.get(username=username)
        emails = user.email_addresses.all()
        email_dict = Email.get_email_dict(emails)

        book_api = BookAPI()
        book = book_api.get_book(isbn, book_title, filetype)

        for lang, emails in email_dict.items():
            book_send_result = book.send(emails=emails, language=lang)

            # raise Exception error if some result is false
            if book_send_result is False:
                raise Exception

    except Exception as e:
        print(f"Error in books.task.send_book_email_task: {e}")
        return False, 400  # status and status_code

    return True, 200
