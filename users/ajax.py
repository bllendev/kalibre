from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.conf import settings
from bookstore_project.logging import log

from users.models import Email
from books.utils import request_is_ajax_bln
from translate.constants import LANGUAGES

import os
import json

import logging
logger = logging.getLogger(__name__)


CustomUser = get_user_model()


def add_email(request):
    is_ajax = request_is_ajax_bln(request)
    try:
        if request.method == 'POST':
            # organize
            post_dict = {key: val for key, val in request.POST.items() if "email_input" in key}
            post_dict_values = list(post_dict.values())

            # extract email info
            email_address = post_dict_values[0]

            # extract user info
            username = request.user.username
            user = CustomUser.objects.get(username=username)

            email, created = Email.objects.get_or_create(address=email_address)
            user.email_addresses.add(email)
            user.save()

            if is_ajax:
                return render(request, 'users/components/email_entry.html', {'email': email, "LANGUAGES": LANGUAGES,})

            # For non-HTMX (no JS) requests:
            return redirect(reverse('my_profile'))
        
        else:
            raise Exception("POST requests only.")

    except Exception as e:
        logger.error(f"ERROR: books.ajax.add_email {e}")
        if is_ajax:
            return HttpResponseServerError("Error adding email.")
        raise e


def delete_email(request, pk):
    try:
        if request.method == 'DELETE':
            # extract user info
            username = request.user.username
            user = CustomUser.objects.get(username=username)
            user_email_to_delete = user.email_addresses.all().filter(pk=pk).first()

            # ensure email exists before deleting
            if not user_email_to_delete:
                return HttpResponseBadRequest("Email not found.")

            # remove/delete email and save user
            user.email_addresses.remove(user_email_to_delete)
            user_email_to_delete.delete()
            user.save()

            # respond with No Content status for HTMX to recognize and remove the <tr>
            return HttpResponse(status=200)

        else:
            raise Exception("DELETE requests only.")
        
    except Exception as e:
        logger.error(f"ERROR: books.ajax.delete_email | {e}")
        raise e

    return HttpResponseBadRequest("Error deleting email.")


def toggle_translate_email(request, pk):
    """Sets the specific Email Model associated with a specific User language to
    translate to when sending ebooks

    params:
       request (POST)

    example:
        list(request.POST.items()) - [('translate_email_pk[]', '7'), ('language_selection', 'bs')]
    """
    is_ajax = request_is_ajax_bln(request)

    try:
        logger.error(f"request.method: {request.method}")
        if is_ajax and request.method == 'POST':
            username = request.user.username
            user = CustomUser.objects.get(username=username)
            email = user.email_addresses.all().get(pk=pk)

            selected_lang_key = f"email_{pk}_language"
            lang_code = request.POST.get(selected_lang_key)

            # set translate and save !
            email.translate_file = lang_code  # NOTE: translate.constants
            email.save()

            if is_ajax:  # if request is coming via HTMX
                return render(request, 'users/components/email_entry.html', {'email': email, "LANGUAGES": LANGUAGES,})

            # for non-HTMX (no JS) requests:
            return reverse('my_profile')
        
        raise Exception("POST requests only.")

    except Exception as e:
        logger.error(f"ERROR: books.ajax.toggle_translate_email | {e}")
        raise e

    return JsonResponse({'status': False}, status=400)
