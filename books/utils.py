import os
import copy
from django.conf import settings
from django.db.models import Q
from django.db import transaction

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
        'links': '',
    }

    def __init__(self, book_api):
        self.author = book_api['Author']
        self.title = book_api['Title']
        self.filetype = book_api['Extension']
        # self.links = [book_api['Mirror_1'], book_api['Mirror_2'], book_api['Mirror_3']]
        self.link = book_api['Mirror_1']
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

    def __init__(self, title_search=None):
        self.libgen = LibgenSearch()
        self.search_query = title_search
        # self.title_first_choice = self.get_title_choices()[0]
        # self._dev_debug()

    def _dev_debug(self):
        pass

    def _book_db_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        books = Book.objects.filter(
            Q(title__icontains=self.search_query) | Q(author__icontains=self.search_query) | Q(filetype__icontains=self.search_query)
        )
        return books

    def _get_title_choices(self):
        # title_filters = {"Extension": "mobi"}
        # titles = self.libgen.search_title_filtered(self.search_query, title_filters, exact_match=False)
        # authors = self.libgen.search_author_filtered(self.search_query, title_filters, exact_match=False)
        import cloudinary.uploader
        from django.conf import settings

        titles = []
        authors = []
        try:
            titles = self.libgen.search_title(self.search_query)
            authors = self.libgen.search_author(self.search_query)
            _book_list = titles + authors
        except Exception as e:
            print(f"_get_title_choices error: {e}")
        return _book_list

    def _get_book_list(self):
        book_list = []
        try:
            # get libgen books
            titles = self._get_title_choices()
            _book_list = [LibgenBook(title) for title in titles]

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
        isbn_log_dict = {book.isbn: book for book in books}
        new_isbn_dict = {}
        if len(books) < 5:
            libgen_books = self._get_book_list()
            books = []
            for new_book in libgen_books:
                new_book_dict = new_book.__dict__
                new_isbn_dict[new_book.isbn] = new_book_dict
            for isbn, new_book_dict in new_isbn_dict.items():
                if isbn not in isbn_log_dict:
                    books.append(Book(**new_book_dict))
            bulk_save(books)

        return books

    def get_book_path_from_link(self, link, book_title, filetype, isbn):
        from django.conf import settings
        import requests

        # get or create book (in db)
        new_book = Book.objects.get(isbn=isbn)          # THESE ISBN SHOULD BE ALL UNIQUE RIGHT ??? @AG++
        if not new_book:
            new_book = Book.objects.filter(title__icontains=book_title, filetype=filetype).first()
        book_download_link = ""

        # get and assign book link
        try:
            if not new_book.link or not new_book.filetype:
                # new book save
                new_book.link = link
                new_book.save()

            # get book download link - this gives us the actual book file
            book_download_link = new_book.get_book_download_link(link)
        except Exception as e:
            print(f"get_book_path_from_link error: {e}")

        # write file to path (will use file to send - then we will delete file)
        new_file_path = os.path.join(settings.BASE_DIR, f"{new_book.title}.{new_book.filetype}")
        with open(new_file_path, "wb") as f:
            if book_download_link:
                temp_book_file_dl = requests.get(book_download_link)
                f.write(temp_book_file_dl.content)
                f.close()
        return new_file_path

    def send_book_file(self, user, link, book_title, filetype, isbn):
        """emails actual book file to recipient addresses"""
        from django.core import mail

        # get book file path
        book_file_path = self.get_book_path_from_link(link, book_title, filetype, isbn)        # web scraper
        if book_file_path is None:
            return

        # send book as email to recipients
        with mail.get_connection() as connection:
            recipient_emails = [email.address for email in user.email_addresses.all()]
            template_message = copy.deepcopy(self.EMAIL_TEMPLATE_LIST)
            template_message[3] = recipient_emails

            email_message = mail.EmailMessage(*tuple(template_message), connection=connection)
            email_message.attach_file(book_file_path)
            email_message.send(fail_silently=False)

        # delete book_file after sending!
        os.remove(book_file_path)


@transaction.atomic
def bulk_save(queryset):
    """atomic save! prevent save issues when saving to db"""
    for item in queryset:
        item.save()
