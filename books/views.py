from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.views.generic import ListView, DetailView
from books.models import Book


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


def _search_results(request):
    from books.utils import LibgenAPI

    query = request.GET.get('q')
    choices = None
    link = None

    if request.method == "POST":
        pass

    if query:
        print(f"QUERY MADE: {query}")
        libgen = LibgenAPI(query)
        choices = libgen.get_title_choices()[0]["Mirror_1"]
        print(f"choices: {choices}")

        # link = libgen.get_first_download_link()

    return render(request, 'books/_search_results.html', {'link': link, 'title_choices': choices})


