from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse, resolve
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from books.models import Book
from users.models import Email
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
    from books.utils import LibgenAPI

    db_query = request.GET.get('db_q')
    if db_query:
        libgen = LibgenAPI(str(db_query), force_api=False)

    api_query = request.GET.get('api_q')
    if api_query:
        libgen = LibgenAPI(str(api_query), force_api=True)

    return render(
        request,
        'books/search_results.html',
        {
            'libgen': libgen,
        }
    )


@never_cache
def my_emails(request):
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


def fx_return_to_sender(request, remove_GET=True):
    """
        Return user back to the url from whence they came.
    """
    request_http_referer = request.META.get("HTTP_REFERER", "")
    if request_http_referer and "?" in request_http_referer and remove_GET:
        request_http_referer = request_http_referer.split("?")[0]
    return redirect(request_http_referer)
