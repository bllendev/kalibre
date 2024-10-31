from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.views.generic import DetailView, View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator


# local
from books.api.book_api import BookAPI
from books.models import Book


@method_decorator(never_cache, name='dispatch')
class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'books/book_detail.html'
    login_url = 'account_login'
    permission_required = 'books.special_status'


@method_decorator(never_cache, name='dispatch')
class GetCover(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        book_id = kwargs.get('pk')
        try:
            book = Book.objects.get(pk=book_id)
            new_cover_html = f'<img src="{book.get_cover_url(set_cover=True)}" alt="{book.title} Cover" class="img-fluid rounded shadow" id="book-cover">'
            return HttpResponse(new_cover_html)
        except Book.DoesNotExist:
            return HttpResponse('Book not found', status=404)
        

class BookSearch(View):
    def get(self, request, original_query):
        query = request.GET.get('q', '')
        if not query:
            query = original_query

        # start with og books
        books = Book.search(original_query)

        return render(
            request,
            'books/components/book_entry_list.html',
            {
                'book_list': Book.search(query, books=books)
            }
        )
    

class BookSearchRefresh(View):
    def post(self, request, original_query):
        book_api = BookAPI(str(original_query), force_api=True)

        book_list = []
        if not book_api:
            raise Exception("BookAPI failed to initialize")

        # get final book list
        book_list = book_api.get_unique_book_list()

        return render(
            request,
            'books/components/book_entry_list.html',
            {
                'book_list': book_list
            }
        )


@never_cache
def search_results(request):
    book_api = None
    original_query = None

    # case 1: user is searching for a book in the database
    db_query = request.POST.get('db_q')
    if db_query:
        book_api = BookAPI(search_query=str(db_query), force_api=False)
        original_query = db_query

    # case 2: user is searching for a book in the api
    api_query = request.POST.get('api_q')
    if api_query:
        book_api = BookAPI(search_query=str(api_query), force_api=True)
        original_query = api_query

    # get final book list
    book_list = []
    if book_api:
        book_list = book_api.get_unique_book_list()

    # prepare translate_book_bln alert for when user sends
    translate_book_bln = False
    if request.user.is_authenticated:
        translate_book_bln = request.user.translate_book_bln

    # hx_confirm_str
    hx_confirm_str = "Be sure to login to send books to you emails!"
    if request.user.is_authenticated:
        hx_confirm_str = "do you want to send this book to the following emails?...\n"
        hx_confirm_str += request.user.email_addresses_str

    return render(
        request,
        'books/search_results.html',
        {
            'original_query': original_query,
            'book_list': book_list,
            'translate_book_bln': translate_book_bln,
            'valid_user': request.user.is_authenticated,
            'hx_confirm_str': hx_confirm_str
        }
    )
