from django.http import JsonResponse
from books.utils import LibgenAPI
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


def send_book(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax and request.method == 'POST':
        # organize
        post_dict = {key: val for key, val in request.POST.items() if "book" in key}
        post_dict_keys = list(post_dict.keys())

        # extract book info
        link = post_dict[post_dict_keys[0]]
        book_title, filetype, isbn = post_dict_keys[0].split("__")
        book_title = book_title.replace("book_", "")
        filetype = filetype.replace("type_", "")
        isbn = isbn.replace("isbn_", "")

        # extract user info
        username = request.user.username
        user = CustomUser.objects.get(username=username)

        # send book file
        libgen = LibgenAPI()
        libgen.send_book_file(user, link, book_title, filetype, isbn)
        return JsonResponse({'status': True}, status=200)

    return JsonResponse({'status': False}, status=400)
