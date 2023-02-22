from django.http import JsonResponse
from books.utils import LibgenAPI
from django.contrib.auth import get_user_model
from users.models import Email


CustomUser = get_user_model()


def send_book(request):
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

        # send book file
        libgen = LibgenAPI()
        libgen.send_book_file(user, json_links, book_title, filetype, isbn)
        return JsonResponse({'status': True}, status=200)

    return JsonResponse({'status': False}, status=400)


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

