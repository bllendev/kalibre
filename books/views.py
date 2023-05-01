from django.shortcuts import render
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from books.models import Book
from django.views.decorators.cache import never_cache


CustomUser = get_user_model()


class BookListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Book
    context_object_name = 'book_list'
    template_name = 'books/book_list.html'
    login_url = 'account_login'
    permission_required = 'books.special_status'


class BookDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    login_url = 'account_login'
    permission_required = 'books.special_status'


@never_cache
def search_results(request):
    from books.libgen_api import LibgenAPI

    db_query = request.GET.get('db_q')
    if db_query:
        libgen = LibgenAPI(str(db_query), force_api=False)

    api_query = request.GET.get('api_q')
    if api_query:
        libgen = LibgenAPI(str(api_query), force_api=True)

    book_list = libgen.get_unique_book_list()

    return render(
        request,
        'books/search_results.html',
        {
            'book_list': libgen.filter_duplicates(book_list),
            'translate_book_bln': request.user.translate_book_bln,
        }
    )


@never_cache
def my_emails(request):
    from books.utils import fx_return_to_sender

    email_addresses = []
    username_str = ''

    if request.user.is_authenticated:
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        email_addresses = user.email_addresses.all()
        username_str = f"{username}'s emails!"

    if request.method == "POST":
        return fx_return_to_sender(request)

    return render(
        request,
        'books/my_emails.html',
        {
            'username_str': username_str,
            'email_addresses': email_addresses,
        }
    )
