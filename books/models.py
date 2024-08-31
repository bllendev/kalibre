# django
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Case, When, Q
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings

# tools
from decouple import config
from functools import reduce
import urllib
import uuid
import requests
import os
import json
import copy
import io

# local
from books.constants import EMAIL_TEMPLATE_LIST
from books.utils import os_silent_remove, send_emails
from books.api._api_openlibrary import OpenLibraryAPI
from translate._translate import EbookTranslate

# logs
from bookstore_project.logging import log
import logging
logger = logging.getLogger(__name__)


class Book(models.Model):
    """
    Represents a single book, containing information such as title, author, and file type.

    This model is related to the :model:`auth.User` through the :model:`Review` model.
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
    cover_url = models.CharField(max_length=144, blank=True, default="")
    cover = models.ImageField(upload_to='covers/', blank=True)
    filetype = models.CharField(max_length=60, default="")  # choices=BOOK_FILETYPE_CHOICES
    isbn = models.CharField(max_length=200, default="")
    json_links = models.JSONField(null=True)

    def __str__(self):
        return f"{self.title} - {self.filetype} - {self.isbn}"
    
    def _set_cover_url(self):
        """sets the cover_url link in db which is used to set the cover images"""
        # setup
        status = None
        openlibrary_api = OpenLibraryAPI()

        # get data
        openlibrary_book = openlibrary_api.get_book(self.isbn)
        cover_id = openlibrary_book["covers"][0]
        cover_url = openlibrary_api.get_cover_url(cover_id)
        if not cover_url:
            raise TypeError("no cover_url was returned !")

        # save to db
        self.cover_url = cover_url
        self.save()
        return cover_url

    def _set_cover(self, cover_url=None):
        """downloads and sets the cover image for the book from the specified URL."""
        cover_url = cover_url if cover_url else self.cover_url
        r = requests.get(cover_url)
        if r.status_code == 200:
            data = r.content
            filename = cover_url.split('/')[-1]
            self.cover.save(filename, ContentFile(data))
            self.save()
        return self.cover

    def get_absolute_url(self):
        """
        returns the URL to access the detail page of this book.
        """
        return reverse('book_detail', args=[str(self.id)])

    def get_json_links(self):
        """
        parses and returns the JSON links associated with the book.
        """
        return json.loads(self.json_links)
    
    def get_cover_url(self, set_cover=False):
        """
        retrieves the URL of the book's cover image. Sets and saves the cover if needed.
        """
        cover = None
        cover_url = os.path.join("/static", "books", "generic_book_cover.jpg")
        try:
            if not self.cover_url or set_cover:
                self._set_cover_url()
                self.refresh_from_db()

            if (self.cover_url and not self.cover) or set_cover:
                self._set_cover()
                self.refresh_from_db()

            if self.cover:
                cover_url = self.cover.url

            else:
                raise Exception("unable to get final image of saved cover.url !")
            logger.info(f"get_cover_url - {cover_url}")
        except Exception as e:
            logger.error(f"get_cover_url | {self} | {e} | {cover_url}")
        return cover_url

    def _get_book_file_download_link(self, link, inner_link_int):
        """scrapes the book file download link from the provided URL."""
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
        book_download_link = None
        try:
            json_links = self.get_json_links()
            book_download_link = self._get_book_file_download_link(json_links[0], inner_link_int)
        except Exception as e:
            book_download_link = self._get_book_file_download_link(json_links[1], 1)
            logging.error(f"_get_book_download_content - BAD LINK: {e}")
        return book_download_link

    def _create_book_file(self, language):
        """
        creates book file from links, will translate if needed

        params:
            - language: language to translate to (if needed)
        returns:
            - path to saved book file (translated if needed)
        """
        # get book file content
        temp_book_file_link = self._get_book_download_content()

        # check book file
        book_file_bln = any([
            self.BOOK_FILETYPE_EPUB in temp_book_file_link,
            self.BOOK_FILETYPE_MOBI in temp_book_file_link,
            self.BOOK_FILETYPE_PDF in temp_book_file_link,
        ])
        if not book_file_bln:
            raise TypeError(f"Book File Boolean must be pdf, epub, or mobi... {temp_book_file_link}")

        # save og file in memory buffer (used as reference for translation as well)
        response = requests.get(temp_book_file_link)
        if response.status_code == 200:
            file_buffer = io.BytesIO(response.content)  # keep the file in an in-memory buffer
        else:
            raise RuntimeError("Failed to download book file")

        # # TRANSLATE FEATURE UNDER CONSTRUCTION FOR NOW @AG++
        # if language and language != "en":
        #     ebook_translate = EbookTranslate(new_file_path, language, google_api=True)
        #     new_file_path = ebook_translate.get_translated_book_path()

        return file_buffer

    def _convert_book_file(self, book_file_path, convert_output_format):
        """
        converts the book file format using an external microservice.

        params:
            - book_file_path: Path to the book file to be converted.
            - convert_output_format: The desired output format (e.g., epub, pdf).
        
        returns:
            Path to the converted book file.
        """
        base_url = config('KALIBRE_EBOOK_CONVERT_URL')
        api_endpoint = "api/convert/"
        url = f"{base_url}{api_endpoint}?output_format={convert_output_format}"
        headers = {
            'X-API-Key': config("KALIBRE_PRIVADO")
        }

        # ensure the file exists
        if not os.path.isfile(book_file_path):
            raise RuntimeError(f"File not found: {book_file_path}")

        # prepare the file to be uploaded
        with open(book_file_path, 'rb') as f:
            files = {'input_file': (os.path.basename(book_file_path), f)}
            response = requests.post(url, headers=headers, files=files)

        # handle the response
        output_path = f"output.{convert_output_format}"
        if response.status_code == 200:
            # Optionally, handle the file response, e.g., save it to disk
            with open(output_path, 'wb') as out:
                out.write(response.content)
            logging.info("Success: File converted and saved.")
        else:
            logging.error("Error:", response.status_code, response.text)
            raise RuntimeError(f"could not convert book_file ! {book_file_path} | {convert_output_format}")

        return output_path

    def get_book_file_path(self, language, convert_output_format=""):
        """
        handles the process of creating and optionally converting a book file.

        params:
            - language: Language for translation.
            - convert_output_format: Format to convert the book file to (optional).
        
        returns:
            path to the processed book file.
        """
        try:
            book_file_buffer = self._create_book_file(language)
            if convert_output_format:
                book_file_buffer = self._convert_book_file(book_file_buffer, convert_output_format)
        except Exception as e:
            logging.error(f"Error processing book file: {e}")
            raise e

        return book_file_buffer

    @log
    def send(self, emails, language="en"):
        """
        wends the book file to the specified emails.

        params:
            - emails: List of email addresses to send the book file to.
            - language: Language for translation (default is 'en').
        
        returns:
            Status of the email sending process.
        """
        book_file_buffer = self.get_book_file_path(language)

        if book_file_buffer:
            template_message = copy.deepcopy(EMAIL_TEMPLATE_LIST)
            template_message[3] = emails
            status = send_emails(template_message, book_file_buffer, self.title)
        else:
            status = False

        return status

    @classmethod
    def search(cls, query, books=None):
        """
        searches for books in the database based on the provided query.

        params:
            - query: The search term(s) to filter books.
            - books: Optional queryset of books to search within.
        
        returns:
            queryset of books matching the search criteria.
        """
        if query:
            query = query.strip()
            search_terms_list = query.split()

            search_terms = []
            exact_match = []
            for term in search_terms_list:
                exact_match.append(Q(title__iexact=term) | Q(author__iexact=term))
                search_terms.extend([
                    Q(title__icontains=term),
                    Q(author__icontains=term),
                    Q(filetype__icontains=term),
                    Q(isbn__icontains=term),
                    Q(_title_lemmatized__icontains=term.replace(" ", "")),
                ])

            # combine the search terms with OR operator
            try:
                search_query = reduce(lambda x, y: x | y, search_terms)
                exact_match_query = reduce(lambda x, y: x | y, exact_match)

                if books is None:
                    books = cls.objects.all()
            
                books = books.annotate(
                    is_exact_match=Case(
                        When(exact_match_query, then=1),
                        default=0,
                        output_field=models.IntegerField()
                    ),
                    title_match=Case(
                        When(Q(title__icontains=query), then=1),
                        default=0,
                        output_field=models.IntegerField(),
                    ),
                    author_match=Case(
                        When(Q(author__icontains=query), then=1),
                        default=0,
                        output_field=models.IntegerField(),
                    )
                ).filter(search_query)

                # order by the new field, so exact matches and then title matches and then author matches come first
                books = books.order_by('-is_exact_match', '-title_match', '-author_match')

            except Exception as e:
                books = cls.objects.none()

        # return query the database to get matching books
        return books

    class Meta:
        indexes = [
            models.Index(fields=['id'], name='id_index'),
        ]
        permissions = [
            ('special_status', 'Can read all books'),
        ]
        ordering = ["-filetype", "-cover_url"]


class Review(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=255)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.review