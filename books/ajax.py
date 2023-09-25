from django.http import JsonResponse
from django.contrib.auth import get_user_model
from users.models import Email
from books.utils import request_is_ajax_bln

import os
import json
import requests


CustomUser = get_user_model()


def send_book_ajax(request):
    """
    - ajax view that sends a book to a user
    - books from libgen are allocated earlier in the flow,
    see LibgenAPI.
    - uses celery task to send book (and translate if needed)
    """
    from books.tasks import send_book_email_task

    if not request_is_ajax_bln(request):
        return JsonResponse({'status': False}, status=400)

    post_dict = {key: val for key, val in request.POST.items() if "book" in key}

    try:
        post_dict_keys = list(post_dict.keys())
        json_links = json.loads(post_dict[post_dict_keys[0]])
        book_title, filetype, isbn = post_dict_keys[0].split("__")
        book_title = book_title.replace("book_", "")
        filetype = filetype.replace("type_", "")
        isbn = isbn.replace("isbn_", "")

        username = request.user.username
    except Exception as e:
        print(f"Error in send_book_ajax_view: {e}")
        return JsonResponse({'status': False}, status=400)

    status, status_code = send_book_email_task.delay(username, book_title, filetype, isbn, json_links)
    return JsonResponse({'status': status}, status=status_code)


def add_email(request):
    is_ajax = request_is_ajax_bln(request)
    if is_ajax and request.method == 'POST':
        # organize
        post_dict = {key: val for key, val in request.POST.items() if "email_input" in key}
        post_dict_values = list(post_dict.values())

        # extract book info
        email = post_dict_values[0]

        # extract user info
        username = request.user.username
        user = CustomUser.objects.get(username=username)

        new_email, created = Email.objects.get_or_create(address=email)
        user.email_addresses.add(new_email)
        user.save()

        return JsonResponse({'status': True, 'email': email, 'email_pk': new_email.pk}, status=200)

    return JsonResponse({'status': False}, status=400)


def delete_email(request):
    is_ajax = request_is_ajax_bln(request)
    if is_ajax and request.method == 'POST':
        # organize
        post_dict = {key: val for key, val in request.POST.items() if 'delete_email_pk' in key}
        post_dict_values = list(post_dict.values())

        email_pk_to_delete = post_dict_values[0]

        # extract user info
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        user_email_to_delete = user.email_addresses.all().filter(pk=email_pk_to_delete).first()

        # delete and save
        user.email_addresses.remove(user_email_to_delete)
        user_email_to_delete.delete()
        user.save()

        return JsonResponse({'status': True, 'delete_email_pk': email_pk_to_delete}, status=200)

    return JsonResponse({'status': False}, status=400)


def toggle_translate_email(request):
    """Sets the specific Email Model associated with a specific User language to
    translate to when sending ebooks

    params:
       request (POST)

    example:
        list(request.POST.items()) - [('translate_email_pk[]', '7'), ('language_selection', 'bs')]
    """
    is_ajax = request_is_ajax_bln(request)
    post_dict = list(request.POST.items())

    if is_ajax and request.method == 'POST' and post_dict:
        # extract email
        email_pk_to_translate__pk__tuple = post_dict[0]
        email_pk_to_translate_pk = email_pk_to_translate__pk__tuple[1]

        # extract language
        language_selection__lang_code__tuple = post_dict[1]
        lang_code = language_selection__lang_code__tuple[1]

        # extract user info and set translate
        username = request.user.username

        try:
            user = CustomUser.objects.get(username=username)
            user_email_to_translate = user.email_addresses.all().get(pk=email_pk_to_translate_pk)

            # set translate and save !
            user_email_to_translate.translate_file = lang_code  # NOTE: translate.constants
            user_email_to_translate.save()

            return JsonResponse({'status': True, 'translate_email_pk': email_pk_to_translate_pk}, status=200)

        except Exception as e:
            print(f"ERROR - toggle_translate_email - {e}")
            return JsonResponse({'status': False}, status=400)

    return JsonResponse({'status': False}, status=400)
