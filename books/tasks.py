from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.db import transaction

from celery import shared_task
from books.api._api_openlibrary import create_or_get_book_from_api
from books.models import Book
from users.models import Email

import logging

logger = logging.getLogger(__name__)


CustomUser = get_user_model()


@shared_task
def send_book_email_task(username, book):
    """
    celery task to send books to associated emails
    """
    user = CustomUser.objects.get(username=username)
    emails = user.email_addresses.all()
    email_dict = Email.get_email_dict(emails)

    for lang, emails in email_dict.items():
        book_send_result = book.send(emails=emails, language=lang)

        # raise Exception error if some result is false
        if book_send_result is False:
            logging.error(
                "books.task.send_book_email_task: Book Failed to send !")
            return False, 400  # status and status_code

    return True, 200


@shared_task
def books_save_vector(book_ids):
    """
    Task to handle saving books with vector embedding consideration.
    """
    with transaction.atomic():
        books = Book.objects.filter(id__in=book_ids)
        for b in books:  # TODO: remove 5 limit cap ?
            b.save(save_vector=True)
