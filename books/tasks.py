from __future__ import absolute_import, unicode_literals

# django
from django.contrib.auth import get_user_model
from django.db import transaction
from celery import shared_task

# local
from books.utils import (
    send_gutenberg_book,
)
from books.models import Book
from users.models import Email

import logging

logger = logging.getLogger(__name__)


CustomUser = get_user_model()


def send_book_gutenberg_email(book_title, username, links):
    user = CustomUser.objects.get(username=username)
    emails = user.email_addresses.all()
    email_dict = Email.get_email_dict(emails)

    for lang, emails in email_dict.items():
        book_send_result = send_gutenberg_book(book_title, links, emails, lang)

        # bail out if some result is false
        if book_send_result is False:
            logging.error("""
                books.task.send_book_gutenberg_email: Book failed to send !
            """)
            return False

    return True


@shared_task
def books_save_vector(book_ids):
    """
    task to handle saving books with vector embedding consideration.
    """
    logger.info(f"books_save_vector ... {len(book_ids)} saved")
    try:
        with transaction.atomic():
            books = Book.objects.filter(id__in=book_ids)
            for b in books:
                b.save(save_vector=True)
    except Exception as e:
        logger.error(e)
        return False, 500
    return True, 200
