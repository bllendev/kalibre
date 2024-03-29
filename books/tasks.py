from __future__ import absolute_import, unicode_literals

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from users.models import Email

from celery import shared_task

import logging
logger = logging.getLogger(__name__)


CustomUser = get_user_model()


@shared_task
def send_book_email_task(username, book):
    """celery task to send books to associated emails
    """
    try:
        user = CustomUser.objects.get(username=username)
        emails = user.email_addresses.all()
        email_dict = Email.get_email_dict(emails)

        for lang, emails in email_dict.items():
            book_send_result = book.send(emails=emails, language=lang)

            # raise Exception error if some result is false
            if book_send_result is False:
                raise Exception(f"Book failed to send! - {book}")

    except Exception as e:
        logging.error(f"books.task.send_book_email_task: {e}")
        return False, 400  # status and status_code

    return True, 200
