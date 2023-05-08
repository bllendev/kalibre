from django.http import JsonResponse
from django.contrib.auth import get_user_model
from users.models import Email

import os
import json
import requests

from books.constants import AI_PROMPT
import openai


CustomUser = get_user_model()


def ai_librarian(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        messages = []

        # be as specific as possible in the behavior it should have
        system_content = f'{AI_PROMPT}. For any other question you must answer "I am only a librarian and I can only answer questions about books."'
        messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": user_message})

        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.4,
        )

        try:
            ai_response = response['choices'][0]['message']['content'].strip()
            print(f"response: {response}")
            print(f"ai_response: {ai_response}")
        except Exception as e:
            print(f"response: {response}")
            print(f"ERROR: {e}")
            print(f"response: {response}")
            print(f"response.json(): {response.json()}")
        return JsonResponse({'message': ai_response})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def send_book_ajax(request):
    """
    - ajax view that sends a book to a user
    - books from libgen are allocated earlier in the flow,
    see LibgenAPI.
    - uses celery tassk to send book (and translate if needed)
    """
    from books.tasks import send_book_ajax_task
    return send_book_ajax_task(request)  # --> celery task


def add_email(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
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
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
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
    from users.models import Email

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    post_dict = {key: val for key, val in request.POST.items() if 'translate_email_pk' in key}
    post_dict_values = list(post_dict.values())

    if is_ajax and request.method == 'POST':
        # organize
        post_dict = {key: val for key, val in request.POST.items() if 'translate_email_pk' in key}
        post_dict_values = list(post_dict.values())
        email_pk_to_translate = post_dict_values[0]

        # extract user info and set translate
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        user_email_to_translate = user.email_addresses.all().get(pk=email_pk_to_translate)

        # set translate and save !
        if user_email_to_translate.translate_file != "":
            user_email_to_translate.translate_file = ""
        else:
            user_email_to_translate.translate_file = Email.TRANSLATE_EN_ES
        user_email_to_translate.save()

        return JsonResponse({'status': True, 'translate_email_pk': email_pk_to_translate}, status=200)

    return JsonResponse({'status': False}, status=400)
