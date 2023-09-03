from django.shortcuts import render
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache

from rest_framework import viewsets


# local
from books.models import Book
from books.serializers import BookSerializer
from translate.constants import LANGUAGES


CustomUser = get_user_model()


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


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
    from books._api import BookAPI

    book_api = None

    # case 1: user is searching for a book in the database
    db_query = request.GET.get('db_q')
    if db_query:
        book_api = BookAPI(str(db_query), force_api=False)

    # case 2: user is searching for a book in the api
    api_query = request.GET.get('api_q')
    if api_query:
        book_api = BookAPI(str(api_query), force_api=True)

    # get final book list
    book_list = []
    if book_api:
        book_list = book_api.get_unique_book_list()

    # prepare translate_book_bln alert for when user sends
    translate_book_bln = False
    if request.user.is_authenticated:
        translate_book_bln = request.user.translate_book_bln

    return render(
        request,
        'books/search_results.html',
        {
            'book_list': book_list,
            'translate_book_bln': translate_book_bln,
        }
    )


@never_cache
def my_emails(request):
    from books.utils import fx_return_to_sender

    # build email_addresses and username_str
    email_addresses = []
    username_str = ''
    if request.user.is_authenticated:
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        email_addresses = user.email_addresses.all()
        username_str = f"{username}'s emails!"

    # handle POST request
    if request.method == "POST":
        return fx_return_to_sender(request)

    return render(
        request,
        'books/my_emails.html',
        {
            'username_str': username_str,
            'email_addresses': email_addresses,
            'LANGUAGES': LANGUAGES,
        }
    )
