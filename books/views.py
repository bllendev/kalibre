from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.http import (
    HttpResponseServerError,
    HttpResponse,
)
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import DetailView, View, TemplateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

# local
from books.models import Book, BookGutenberg
from books.api._api_openlibrary import (
    OpenLibraryAPI,
    get_or_create_book_from_api,
)
from books.tasks import (
    send_book_gutenberg_email,
)

# logging
import logging

logger = logging.getLogger(__name__)

CustomUser = get_user_model()


@method_decorator(never_cache, name="dispatch")
class BookSaveVectorView(View):
    def post(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        book.save(save_vector=True)
        return HttpResponse()


@method_decorator(never_cache, name="dispatch")
class BookSearchOpenlibraryView(View):
    """
    pings openlibrary api with query
    ... conditional if inital response on search results was too
    few, seperate process to populate list asynchronouly"
    ... filters out books which exist as gutenberg book
    """

    def post(self, request, *args, **kwargs):
        """
        NOTE: post because we get_or_create books from openlibrary
        ... (as of now)
        """
        logger.info("BookSearchOpenlibraryView...")
        query = request.POST.get("query")

        open_library_api = OpenLibraryAPI()
        book_list = open_library_api.fetch_books(query)[:20]
        if not book_list:
            return HttpResponseServerError(405, "no books found!")

        books = list()
        books_to_vector_save = list()
        with transaction.atomic():
            for b in book_list:
                b, created = get_or_create_book_from_api(b)
                books.append(b)

                # add to vector save list
                if created:
                    books_to_vector_save.append(b)

        # render response
        response = render(
            request, "books/components/book_entry_list.html", {
                "book_list": books}
        )

        return response


@method_decorator(never_cache, name="dispatch")
class BookSearchView(View):
    """
    - searches via pg_vector
    - NOTE: returns only gutenberg open source books as labeled in db
    """

    template_name = "books/components/book_entry_list.html"  # includes book_entry.html

    def get(self, request, query=None, *args, **kwargs):
        query = request.GET.get("query", query)
        q = request.GET.get("q", "")  # further filter query
        books = list()

        if query:
            books = Book.search(query, gutenberg=True)

        if q:
            # TODO: consider fuzzy match for further filtering
            books = Book.search(q, books, gutenberg=True)

        # render books html
        return render(request, self.template_name, {"book_list": books})


@method_decorator(never_cache, name="dispatch")
class SearchResultsView(TemplateView):
    """
    the main search result template view, we then load in respective
    search result apis via decoupled components upon load
    """

    template_name = "books/search_results.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # prepare translate_book_bln alert for when user sends
        translate_book_bln = False
        if self.request.user.is_authenticated:
            translate_book_bln = self.request.user.translate_book_bln

        # create an hx_confirm_str message
        hx_confirm_str = "Be sure to login to send books to your emails!"
        if self.request.user.is_authenticated:
            hx_confirm_str = (
                "Do you want to send this book to the following emails?...\n"
            )
            hx_confirm_str += self.request.user.email_addresses_str

        # add to the context
        context["translate_book_bln"] = translate_book_bln
        context["hx_confirm_str"] = hx_confirm_str
        context["query"] = self.query
        return context

    def get(self, request, query="", *args, **kwargs):
        self.query = request.GET.get("query", query)
        response = super().get(request, *args, **kwargs)
        return response


# book views
@method_decorator(never_cache, name="dispatch")
class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    context_object_name = "book"
    template_name = "books/book_detail.html"


@method_decorator(never_cache, name="dispatch")
class GetCoverView(LoginRequiredMixin, View):
    """NOTE: lazily getting the cover url will also query
    and save to db if img doesn't exist.
    """

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("pk")
        try:
            book = Book.objects.get(pk=book_id)
            new_cover_html = f"""
               <img src="{book.get_cover_url(set_cover=True)}"
               alt="{book.title} Cover" class="img-fluid rounded shadow"
               id="book-cover">
            """
            return HttpResponse(new_cover_html)
        except Book.DoesNotExist:
            return HttpResponse("Book not found", status=404)


@method_decorator(never_cache, name="dispatch")
class SendBookGutenbergView(LoginRequiredMixin, View):
    """ """

    def post(self, request, pk, *args, **kwargs):
        # add code here...
        try:
            link = request.POST.get("link", None)
            if not link:
                logger.error("No book data found in the request.")
                error = "Missing link from Gutenberg Book."
                return HttpResponseServerError(error)

            # get book
            book = Book.objects.get(pk=pk)

            # get user info
            username = request.user.username
            user = CustomUser.objects.get(username=username)

            # book send task here
            status_bln = send_book_gutenberg_email(book.title, username, link)

            # if book sent - add to users my_books ! else raise error
            if status_bln:
                user.my_books.add(book)
                user.save()

            return HttpResponse("Successfully Sent!", status=200)

        except CustomUser.DoesNotExist as e:
            logger.error(e)
            signup_url = f"{reverse('account_signup')}"
            signup_url += f"?next={request.get_full_path()}"
            return redirect(signup_url)

        except Book.DoesNotExist as e:
            logger.error(e)
            return HttpResponseServerError(
                "Error sending book, the book didn't seem to 'exist'."
            )

        except Exception as e:
            logger.error(f"ERROR: SendBookGutenbergView {e}")
            return HttpResponseServerError("Error sending book.")


@method_decorator(never_cache, name="dispatch")
class GetGutenbergLinksView(LoginRequiredMixin, View):
    template_name = "books/components/dropdown_gutenberg_links.html"

    def get_context_data(self, *args, **kwargs):
        context = dict()

        # prepare translate_book_bln alert for when user sends
        translate_book_bln = False
        if self.request.user.is_authenticated:
            translate_book_bln = self.request.user.translate_book_bln

        # create an hx_confirm_str message
        hx_confirm_str = "Be sure to login to send books to your emails!"
        if self.request.user.is_authenticated:
            hx_confirm_str = (
                "Do you want to attempt to send this book to the following emails?...\n"
            )
            hx_confirm_str += self.request.user.email_addresses_str

        # add to the context
        context["translate_book_bln"] = translate_book_bln
        context["hx_confirm_str"] = hx_confirm_str
        return context

    def get(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        # search gutenberg books for links
        gutenberg_books = BookGutenberg.objects.filter(
            title__icontains=book.title)
        # return fuzzy matched book links
        context = self.get_context_data()
        context["book"] = book
        context["gutenberg_books"] = gutenberg_books
        return render(request, self.template_name, context)
