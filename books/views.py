from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import (
    HttpResponseServerError,
    HttpResponse,
)
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import DetailView, View, TemplateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
import json

# localviews
from books.models import Book
from books.api._api_openlibrary import (
    OpenLibraryAPI,
    create_or_get_book_from_api,
)
from books.tasks import books_save_vector, send_book_email_task

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
    ... books are saved to db along with embeddings,
    authors, and publications (soon)
    ... conditional if inital response on search results was too
    few, seperate process to populate list asynchronouly"
    """

    def post(self, request, *args, **kwargs):
        logger.info("BookSearchOpenlibraryView...")
        query = request.POST.get("query")
        open_library_api = OpenLibraryAPI()
        book_list = open_library_api.fetch_books(query)[:20]
        if not book_list:
            return HttpResponseServerError(405, "no books found!")

        # TODO: make this use celery
        books = list()
        books_to_vector_save = list()
        with transaction.atomic():
            for b in book_list:
                b, created = create_or_get_book_from_api(b)
                books.append(b)

                # add to vector save list
                if created:
                    books_to_vector_save.append(b)

        # prepare list of ids of books we want to vector save
        books_to_vector_save_ids = []
        if books_to_vector_save:
            books_to_vector_save_ids = [str(b.id)
                                        for b in books_to_vector_save]

        # render response
        response = render(
            request, "books/components/book_entry_list.html", {
                "book_list": books}
        )

        # trigger vector save background process!
        if books_to_vector_save_ids:
            response["HX-Trigger-After-Settle"] = json.dumps(
                {"book-save-vector": books_to_vector_save_ids}
            )

        return response


@method_decorator(never_cache, name="dispatch")
class BookSearchView(View):
    """
    - searches via pg_vector, trigger BookSearchOpenlibraryView if few results
    """

    def get(self, request, query=None, *args, **kwargs):
        # get book list
        query = request.GET.get("query", query)
        q = request.GET.get("q", "")
        trigger = request.GET.get("trigger", "")

        book_list = list()
        if query:
            # query and filter
            book_list = Book.search(query)

        if q:
            book_list = Book.search(q, book_list)

        # trigger setup
        if len(book_list) > 5 or trigger:
            trigger = ""

        # render books html
        response = render(
            request, "books/components/book_entry_list.html", {
                "book_list": book_list}
        )

        response["HX-Trigger-After-Swap"] = trigger
        return response


@method_decorator(never_cache, name="dispatch")
class SearchResultsView(TemplateView):
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
class SendBookView(LoginRequiredMixin, View):
    """
    - books from libgen are allocated earlier in the flow,
    see LibgenAPI.
    - uses celery task to send book (and translate if needed)
    """

    def post(self, request, pk, *args, **kwargs):
        # check authenticated user, send to login w/ next if not authenticated
        if not request.user.is_authenticated:
            # TODO: fix this such that we use hidden input, not rely on user entered url
            next_url = request.get_full_path()
            login_with_next_url = f"{reverse('account_login')}?next={next_url}"
            return redirect(login_with_next_url)

        try:
            # organize
            book = Book.objects.get(pk=pk)

            # extract user info
            username = request.user.username
            user = CustomUser.objects.get(username=username)

            # book send task here
            status_bln, _ = send_book_email_task.delay(username, book)

            # if book sent - add to users my_books ! else raise error
            if status_bln:
                user.my_books.add(book)
                user.save()
            else:
                raise RuntimeError(f"{book}, failed to send!")

            return HttpResponse(status=200)

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

        except RuntimeError as e:
            logger.error(e)
            return HttpResponseServerError("Error sending book.")

        except Exception as e:
            logger.error(f"ERROR: SendBookView {e}")
            return HttpResponseServerError("Error sending book.")
