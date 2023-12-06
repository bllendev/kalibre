from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django.conf import settings
from bookstore_project.logging import log

from users.models import Email
from books.models import Book
from books.utils import request_is_ajax_bln, fx_return_to_sender
from translate.constants import LANGUAGES

import os
import json

import logging
logger = logging.getLogger(__name__)


CustomUser = get_user_model()


def send_book_ajax(request, pk):
    """
    - ajax view that sends a book to a user
    - books from libgen are allocated earlier in the flow,
    see LibgenAPI.
    - uses celery task to send book (and translate if needed)
    """
    from books.tasks import send_book_email_task
    from books.api.book_api import BookAPI

    # check authenticated user, send to login with next if not authenticated
    if not request.user.is_authenticated:
        return redirect(f"{reverse('account_login')}?next={request.get_full_path()}")

    try:
        if request.method == 'POST':
            # organize
            book = Book.objects.get(pk=pk)

            # extract user info
            username = request.user.username
            user = CustomUser.objects.get(username=username)

            # book send task here
            status_bln, status_code = send_book_email_task(username, book)            

            # if book sent - add to users my_books ! else raise error
            if status_bln:
                user.my_books.add(book)
                user.save()
            else:
                raise RuntimeError(f"{book}, failed to send!")

            return HttpResponse(status=200)

        else:
            raise Exception("POST requests only.")

    except CustomUser.DoesNotExist as e:
        logger.error(e)
        return redirect(f"{reverse('account_signup')}?next={request.get_full_path()}")

    except Book.DoesNotExist as e:
        logger.error(e)
        return HttpResponseServerError("Error sending book.")
    
    except RuntimeError as e:
        logger.error(e)
        return HttpResponseServerError("Error sending book.")

    except Exception as e:
        logger.error(f"ERROR: books.ajax.send_book_ajax {e}")
        return HttpResponseServerError("Error sending book.")
