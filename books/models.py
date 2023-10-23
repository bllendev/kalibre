# django
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.conf import settings

# tools
import urllib
import uuid
import requests
import os
import json
import copy

# local
from books.constants import EMAIL_TEMPLATE_LIST
from books.managers import BookManager
from books.utils import os_silent_remove, send_emails
from translate._translate import EbookTranslate


class Book(models.Model):
    """
    - All APIBooks become a Book model object
    - we lemmatize the title of our books to improve searching,
    and to prevent duplicates as much as we can
    """
    BOOK_FILETYPE_EPUB = "epub"
    BOOK_FILETYPE_MOBI = "mobi"
    BOOK_FILETYPE_PDF = "pdf"
    # BOOK_FILETYPE_CHOICES = (
    #     (BOOK_FILETYPE_EPUB, BOOK_FILETYPE_EPUB),
    #     (BOOK_FILETYPE_MOBI, BOOK_FILETYPE_MOBI),
    #     (BOOK_FILETYPE_PDF, BOOK_FILETYPE_PDF),
    # )

    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid.uuid4,
        editable=False,
    )

    title = models.CharField(max_length=500)
    _title_lemmatized = models.CharField(max_length=500, default="")        # see LibgenBook.init()
    author = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    cover = models.ImageField(upload_to='covers/', blank=True)
    filetype = models.CharField(max_length=60, default="")  # choices=BOOK_FILETYPE_CHOICES
    isbn = models.CharField(max_length=200, default="")
    json_links = models.JSONField(null=True)

    objects = BookManager()

    def __str__(self):
        return f"{self.title} - {self.filetype} - {self.isbn}"

    @property
    def ssn(self):  # NOTE: see send_book_email_task
        return f"book_{self.title}__type_{self.filetype}__isbn_{self.isbn}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])
    
    def get_cover_url(self):
        cover_url = os.path.join("/static", "books", "generic_book_cover.jpg")
        if self.cover:
            cover_url = self.cover.url
        return cover_url


    def _get_book_file_download_link(self, link, inner_link_int):
        import collections
        collections.Callable = collections.abc.Callable
        from bs4 import BeautifulSoup

        book_download_link = None
        with urllib.request.urlopen(link) as response:
            soup = BeautifulSoup(response.read(), "html.parser")
            book_download_link = soup.find_all('a')[inner_link_int].get('href')
        return book_download_link

    def _get_book_download_content(self, inner_link_int=1):
        """
            - this takes scraps self.link, finding the
            specific download link to the book file.
        """
        try:
            json_links = json.loads(self.json_links)
            book_download_link = self._get_book_file_download_link(json_links[0], inner_link_int)
        except Exception as e:
            book_download_link = self._get_book_file_download_link(json_links[1], 1)
            print(f"_get_book_download_content - BAD LINK: {e}")
        return book_download_link

    def _create_book_file(self, new_file_path, language):
        """
        creates book file from links, will translate if needed

        params:
            - new_file_path: path to save book file
            - language: language to translate to (if needed)
        returns:
            - path to saved book file (translated if needed)
        """
        # set final_path
        book_final_path = ""

        # get book file content
        temp_book_file_link = self._get_book_download_content()
        temp_book_file_dl = requests.get(temp_book_file_link)

        # write book file content
        try:

            # check book file
            book_file_bln = any([
                self.BOOK_FILETYPE_EPUB in temp_book_file_link,
                self.BOOK_FILETYPE_MOBI in temp_book_file_link,
                self.BOOK_FILETYPE_PDF in temp_book_file_link,
            ])
            if not book_file_bln:
                raise TypeError

            # save og file (used as reference for translation as well)
            with temp_book_file_dl and open(new_file_path, "wb") as f:
                f.write(temp_book_file_dl.content)
                f.close()

            # TRANSLATE FEATURE UNDER CONSTRUCTION FOR NOW @AG++
            if language != "en":
                ebook_translate = EbookTranslate(new_file_path, language, google_api=True)
                new_file_path = ebook_translate.get_translated_book_path()

            # set final book path
            book_final_path = new_file_path

        except TypeError as e:
            print(f"{e}: temp_book_file_link is not an allowable book file type... {temp_book_file_link}")

        except Exception as e:
            # attempt removal in case of error
            os_silent_remove(new_file_path)

            # debug
            print(f"ERROR OCCURED: {e}")
            print(f"self BOOK @@@!!!: {self}")
            print(f"new_file_path: {new_file_path}")
            print(f"json_links: {self.json_links}")
            print(f"temp_book_file_link: {temp_book_file_link}")
            print(f"temp_book_file_dl: {temp_book_file_dl}")
            print(f"langauge: {language}")
            print("---------------------")
            raise e

        return book_final_path

    def get_book_file_path(self, language):
        # write file to path (will use file to send - then we will delete file)
        title = self.title.replace("/", "-").replace("//", "-").replace("\\", "-")
        new_file_path = os.path.join(settings.BASE_DIR, f"{title}.{self.filetype}")

        # create book file
        book_file_path = self._create_book_file(new_file_path, language)
        return book_file_path

    def send(self, emails, language="en"):
        """emails actual book file to recipient addresses"""
        book_file_path = self.get_book_file_path(language)
        template_message = copy.deepcopy(EMAIL_TEMPLATE_LIST)
        template_message[3] = emails
        status = send_emails(template_message, [book_file_path])
        return status

    # class Meta:
    #     indexes = [
    #         models.Index(fields=['id'], name='id_index'),
    #     ]
    #     permissions = [
    #         ('special_status', 'Can read all books'),
    #     ]


class Review(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=255)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.review