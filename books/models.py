from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import JSONField
from django.conf import settings

import urllib
import uuid
import requests
import os
import json
import copy

from books.constants import EMAIL_TEMPLATE_LIST
from books.managers import BookManager
from books.utils import os_silent_remove
from translate._translate import EbookTranslate


class Book(models.Model):
    """
    - All APIBooks become a Book model object
    - we lemmatize the title of our books to improve searching,
    and to prevent duplicates as much as we can
    """

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
    filetype = models.CharField(max_length=60, default="")
    isbn = models.CharField(max_length=200, default="")
    json_links = models.JSONField(null=True)

    objects = BookManager()

    def __str__(self):
        return f"{self.title} - {self.filetype} - {self.isbn}"

    @property
    def ssn(self):
        return f"book_{self.title}__type_{self.filetype}__isbn_{self.isbn}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])

    def _get_book_file_download_link(self, link, inner_link_int):
        from bs4 import BeautifulSoup
        book_download_link = None
        with urllib.request.urlopen(link) as response:
            soup = BeautifulSoup(response.read(), "html.parser")
            book_download_link = soup.find_all('a')[inner_link_int].get('href')
            print(f"book_download_link: {book_download_link}")
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
        # get book file content
        temp_book_file_link = self._get_book_download_content()
        temp_book_file_dl = requests.get(temp_book_file_link)

        # debug
        # print(f"self BOOK @@@!!!: {self}")
        # print(f"new_file_path: {new_file_path}")
        # print(f"json_links: {self.json_links}")
        # print(f"temp_book_file_link: {temp_book_file_link}")
        # print(f"temp_book_file_dl: {temp_book_file_dl}")
        # print(f"langauge: {language}")
        # print(f"----------------------------------")

        # write book file content
        try:

            # save og file (used as reference for translation as well)
            ebook_translated_path = new_file_path
            with temp_book_file_dl and open(new_file_path, "wb") as f:
                f.write(temp_book_file_dl.content)
                f.close()

            # TRANSLATE FEATURE UNDER CONSTRUCTION FOR NOW @AG++
            if language != "en":
                ebook_translate = EbookTranslate(new_file_path, language, google_api=True)
                ebook_translated_path = ebook_translate.get_translated_book_path()

        except Exception as e:
            print(f"ERROR OCCURED: {e}")
            os_silent_remove(new_file_path)    # attempt removal in case of error (make sure we are keeping repo clean)
            raise e

        return ebook_translated_path

    def get_book_file_path_from_links(self, language):
        # write file to path (will use file to send - then we will delete file)
        title = self.title.replace("/", "-").replace("//", "-").replace("\\", "-")
        new_file_path = os.path.join(settings.BASE_DIR, f"{title}.{self.filetype}")

        # create book file
        book_file_path = self._create_book_file(new_file_path, language)
        return book_file_path

    def send(self, email_list, language="en"):
        """emails actual book file to recipient addresses"""
        from django.core import mail

        # get book file path (safety bypass if no path)
        book_file_path = self.get_book_file_path_from_links(language)  # web scraper
        if book_file_path is None:
            return

        # send book as email to recipients
        with mail.get_connection() as connection:
            template_message = copy.deepcopy(EMAIL_TEMPLATE_LIST)  # NOTE: deep copy
            template_message[3] = email_list

            email_message = mail.EmailMessage(*tuple(template_message), connection=connection)
            email_message.attach_file(book_file_path)
            email_message.send(fail_silently=False)

        # delete book_file after sending!
        os_silent_remove(book_file_path)

    class Meta:
        indexes = [
            models.Index(fields=['id'], name='id_index'),
        ]
        permissions = [
            ('special_status', 'Can read all books'),
        ]

class Review(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=255)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.review