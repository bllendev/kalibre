import os
import copy
from django.conf import settings
from django.db.models import Q
from django.db import transaction
import json

from books.models import Book
from books.libgen_api import LibgenSearch


class LibgenBook:
    """
        - a handy class that streamlines our scraped
        libgen api books into a nice accessible class
        for our Book model
    """

    BOOK_TEMPLATE = {
        'id': '',
        'title': '',
        'author': '',
        'filetype': '',
        'json_links': '',
    }

    def __init__(self, book_api):
        self.author = book_api['Author']
        self.title = book_api['Title']
        self.filetype = book_api['Extension']
        self.json_links = json.dumps([book_api['Mirror_1'], book_api['Mirror_2'], book_api['Mirror_3']])
        # self.link = book_api['Mirror_1']
        self.isbn = book_api['ID']


class LibgenAPI:

    LIBGEN_COLS = [
        "ID",
        "Author",
        "Title",
        "Publisher",
        "Year",
        "Pages",
        "Language",
        "Size",
        "Extension",
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
        "Mirror_5",
        "Edit",
    ]

    EMAIL_TEMPLATE_LIST = [
        '',                      # empty subject line
        '',                  # empty message line
        str(settings.DEFAULT_FROM_EMAIL),        # from email
        list(),                             # recipient_list
    ]

    STABLE_FILE_TYPES = {"epub", "mobi"}

    def __init__(self, title_search=None, force_api=False):
        self.libgen = LibgenSearch()
        self.search_query = title_search
        self.force_api = force_api
        # self.title_first_choice = self.get_title_choices()[0]
        # self._dev_debug()

    def _dev_debug(self):
        pass

    def _book_db_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        books = Book.objects.filter(
            Q(title__icontains=self.search_query) | Q(author__icontains=self.search_query) | Q(filetype__icontains=self.search_query) | Q(isbn__icontains=self.search_query)
        )
        return books

    def _get_api_book_choices(self):
        # title_filters = {"Extension": "mobi"}
        # titles = self.libgen.search_title_filtered(self.search_query, title_filters, exact_match=False)
        # authors = self.libgen.search_author_filtered(self.search_query, title_filters, exact_match=False)
        from django.conf import settings

        titles = []
        authors = []
        _book_list = []
        try:
            titles = self.libgen.search_title(self.search_query)
            authors = self.libgen.search_author(self.search_query)
            _book_list = titles + authors
        except Exception as e:
            print(f"_get_api_book_choices error: {e}")
        return _book_list

    def _get_book_list(self):
        book_list = []
        try:
            # get libgen books
            api_book = self._get_api_book_choices()
            _book_list = [LibgenBook(api_book) for api_book in api_book]

            # filter by stable files for now (epub, mobi) - will eventually add .pdf and filter/selection system to ui - @AG
            book_list = [book for book in _book_list if book.filetype in self.STABLE_FILE_TYPES]

        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            return book_list

    def get_book_list(self):
        # check books in db first
        books = self._book_db_search()

        # if not reasonable selection, do fresh query using libgen api
        if not books or self.force_api:
            db_books_by_id = {book.isbn: book for book in books}    
            api_books_by_id = {book.isbn: book.__dict__ for book in self._get_book_list()}
            created_books_by_id = {}

            # filter books by what is already in our db (if any)
            for isbn, new_book_dict in api_books_by_id.items():
                if isbn not in db_books_by_id:
                    book_obj = Book(**new_book_dict)
                    created_books_by_id[isbn] = book_obj

            # save filtered books
            books = {book for isbn, book in created_books_by_id.items()}
            bulk_save(books)

        return books

    def get_book_file_path_from_links(self, links, book_title, filetype, isbn):
        from django.conf import settings
        import requests

        # get book !
        new_book = Book.objects.filter(isbn=isbn).first()          # THESE ISBN SHOULD BE ALL UNIQUE RIGHT ??? @AG++
        if not new_book:
            new_book = Book.objects.filter(title__icontains=book_title, filetype=filetype).first()

        # write file to path (will use file to send - then we will delete file)
        book_file_str = f"{new_book.title}.{new_book.filetype}"
        new_file_path = os.path.join(settings.BASE_DIR, book_file_str)

        i = 0
        temp_book_file_dl = None
        while not temp_book_file_dl and i < len(links):
            temp_book_file_dl = new_book.get_book_download_content(links[i])
            i += 1
        try:
            with open(new_file_path, "wb") as f:
                f.write(temp_book_file_dl.content)
                f.close()
        except Exception as e:
            os_silent_remove(new_file_path)    # attempt removal in case of error (make sure we are keeping repo clean)
        return new_file_path

    def send_book_file(self, user, links, book_title, filetype, isbn):
        """emails actual book file to recipient addresses"""
        from django.core import mail

        # get book file path (safety bypass if no path)
        book_file_path = self.get_book_file_path_from_links(links, book_title, filetype, isbn)        # web scraper
        if book_file_path is None:
            return

        # send book as email to recipients
        with mail.get_connection() as connection:
            recipient_emails = [email.address for email in user.email_addresses.all()]
            template_message = copy.deepcopy(self.EMAIL_TEMPLATE_LIST)                        # NOTE: deep copy
            template_message[3] = recipient_emails

            email_message = mail.EmailMessage(*tuple(template_message), connection=connection)
            email_message.attach_file(book_file_path)
            email_message.send(fail_silently=False)

        # delete book_file after sending!
        os_silent_remove(book_file_path)


@transaction.atomic
def bulk_save(queryset):
    """atomic save! prevent save issues when saving to db"""
    for item in queryset:
        item.save()


def os_silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred
