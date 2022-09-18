import os
import copy
from libgen_api import LibgenSearch
from django.conf import settings


class LibgenBook:
    BOOK_TEMPLATE = {
        'id': '',
        'title': '',
        'author': '',
        'file_type': '',
        'links': '',
    }

    def __init__(self, book_api):
        self.author = book_api['Author']
        self.title = book_api['Title']
        self.file_type = book_api['Extension']
        self.links = [book_api['Mirror_1'], book_api['Mirror_2'], book_api['Mirror_3']]
        self.id = book_api['ID']


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

    def __init__(self, title_search=None):
        self.libgen = LibgenSearch()
        self.title_search = title_search
        # self.title_first_choice = self.get_title_choices()[0]

    def _get_title_choices(self):
        title_filters = {"Extension": "mobi"}
        # titles = self.libgen.search_title_filtered(self.title_search, title_filters, exact_match=False)
        # authors = self.libgen.search_author_filtered(self.title_search, title_filters, exact_match=False)
        titles = self.libgen.search_title(self.title_search)
        authors = self.libgen.search_author(self.title_search)
        return titles + authors

    def get_book_list(self):
        STABLE_FILE_TYPES = {"epub", "mobi"}
        book_list = []
        try:
            _book_list = [LibgenBook(title) for title in self._get_title_choices()]
            book_list = [book for book in _book_list if book.file_type in STABLE_FILE_TYPES]
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            return book_list

    def download_book(self, user, link, book_title, filetype):
        from django.core import mail

        book_file_path = self.get_book_from_link(link, book_title, filetype)        # web scraper
        if book_file_path is None:
            return

        with mail.get_connection() as connection:
            recipient_emails = [email.address for email in user.email_address.all()]
            print(f"recipient_emails: {recipient_emails}")
            template_message = copy.deepcopy(self.EMAIL_TEMPLATE_LIST)
            template_message[3] = recipient_emails + ["allenfg86@gmail.com"]

            email_message = mail.EmailMessage(*tuple(template_message), connection=connection)
            email_message.attach_file(book_file_path)
            email_message.send(fail_silently=False)

        os.remove(book_file_path)
        # # DEBUG
        # print(f"email!!!: {email_message}")
        # print(f"link: {link}")
        # print(f"USER!!! {user}")
        # print(f"recipient emails!: {recipient_emails}")

    def get_book_from_link(self, link, book_title, filetype):
        from bs4 import BeautifulSoup
        import requests
        from django.conf import settings
        from books.models import Book

        new_book, created = Book.objects.get_or_create(title=book_title, filetype=filetype)
        book_dl_link = ""
        book_dl_filetype = ""
        if not new_book.link or not new_book.filetype:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            first_book_dl_link = soup.find_all('a')[0].get('href')
            new_book.link = first_book_dl_link
            new_book.filetype = filetype
            new_book.save()

        new_file_path = os.path.join(settings.BASE_DIR, f"{new_book.title}.{new_book.filetype}")
        with open(new_file_path, "wb") as f:
            if first_book_dl_link:
                temp_book_file_dl = requests.get(first_book_dl_link)
                f.write(temp_book_file_dl.content)
        return new_file_path
