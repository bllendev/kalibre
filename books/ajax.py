from django.http import JsonResponse
from django.contrib.auth import get_user_model
from users.models import Email


CustomUser = get_user_model()


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
