from django.http import HttpResponseBadRequest, JsonResponse

from todos.models import Todo


def todos(request):
    # request.is_ajax() is deprecated since django 3.1
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            username = request.user.username
            user = CustomUser.objects.get(username=username)
            libgen = LibgenAPI()
            book_link = request.POST.get('book')
            libgen.download_book(user, book_link)
            return JsonResponse({'context': todos})
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')