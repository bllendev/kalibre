from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse, resolve
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from books.models import Book
from users.models import Email


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


def search_results(request):
    from books.utils import LibgenAPI

    query = request.GET.get('q')
    choices_list = None
    link = None

    if request.method == "POST":
        for key, val in request.POST.items():
            if "book" in key:
                link = val
                book_title = key.replace("book_", "")
                username = request.user.username
                user = CustomUser.objects.get(username=username)
                libgen = LibgenAPI()
                libgen.download_book(user, link, book_title)
                return redirect(reverse("home"))

    if query:
        libgen = LibgenAPI(str(query))
        choices_list = libgen._get_title_choices()

    return render(
        request,
        'books/search_results.html',
        {
            'link': link,
            'choices_list': choices_list,
            'libgen': libgen,
        }
    )


def my_emails(request):
    email_addresses = []
    if request.user.is_authenticated:
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        email_addresses = user.email_address.all()

    if request.method == "POST":
        if user:
            email = request.POST.get('email')
            new_email = Email(address=email)
            new_email.save()
            if user.email_address.exists():
                user.email_address.add(new_email)
            else:
                user.email_address.set({new_email})
            user.save()
            print("POST REQUEST HIT YUP")
            return redirect(reverse("my_emails"))

    print(CustomUser.__dict__)
    return render(
        request,
        'books/my_emails.html',
        {
            'email_addresses': email_addresses,
        }
    )

