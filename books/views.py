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


class SearchResultsListView(ListView):
    model = Book
    context_object_name = 'book_list'
    template_name = 'books/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))


@never_cache
def search_results(request):
    from books.utils import LibgenAPI

    query = request.GET.get('q')
    choices_list = None

    if query:
        libgen = LibgenAPI(str(query))
        choices_list = libgen._get_title_choices()

    return render(
        request,
        'books/search_results.html',
        {
            'choices_list': choices_list,
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
        if user:
            if request.POST.get("delete_email"):
                email = request.POST.get("delete_email")
                user_email = user.email_addresses.all().filter(address=email).first()
                if user_email:
                    user.email_addresses.remove(user_email)
                    user_email.delete()
            if request.POST.get("add_email"):
                email = request.POST.get('add_email')
                new_email, created = Email.objects.get_or_create(address=email)
                new_email.user = user
                user.email_addresses.add(new_email)
            user.save()
            return fx_return_to_sender(request)

    return render(
        request,
        'books/my_emails.html',
        {
            'username_str': username_str,
            'email_addresses': email_addresses,
        }
    )


def get_absolute_dict(request):
    urls = {
        'ABSOLUTE_ROOT': request.build_absolute_uri('/')[:-1].strip("/"),
        'ABSOLUTE_ROOT_URL': request.build_absolute_uri('/').strip("/"),
    }

    return urls


def fx_return_to_sender(request, remove_GET=True):
    """
        Return user back to the url from whence they came.
    """
    request_http_referer = request.META.get("HTTP_REFERER", "")
    print(f"request_http_referer: {request_http_referer}")
    if request_http_referer and "?" in request_http_referer and remove_GET:
        request_http_referer = request_http_referer.split("?")[0]
        print(f"SECOND request_http_referer: {request_http_referer}")
    return redirect(request_http_referer)
