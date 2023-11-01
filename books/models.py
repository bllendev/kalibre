# django
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Case, When, Q
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings

# tools
from functools import reduce
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
from books.api._api_openlibrary import OpenLibraryAPI
from translate._translate import EbookTranslate

# logs
import logging
logger = logging.getLogger(__name__)


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
    cover_url = models.CharField(max_length=144, blank=True, default="")
    cover = models.ImageField(upload_to='covers/', blank=True)
    filetype = models.CharField(max_length=60, default="")  # choices=BOOK_FILETYPE_CHOICES
    isbn = models.CharField(max_length=200, default="")
    json_links = models.JSONField(null=True)

    objects = BookManager()

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
        cover_url = openlibary_api.get_cover_url(cover_id)
        if not cover_url:
            raise TypeError("no cover_url was returned !")

        # save to db
        self.cover_url = cover_url
        self.save()
        return

    def _set_cover(self, cover_url):
        cover_url = cover_url if cover_url else self.cover_url
        r = requests.get(self.cover_url)
        if r.status_code == 200:
            data = r.content
            filename = self.cover_url.split('/')[-1]
            self.cover.save(filename, ContentFile(data))
            self.save()
        return self.cover

    @property
    def ssn(self):  # NOTE: see send_book_email_task
        return f"book_{self.title}__type_{self.filetype}__isbn_{self.isbn}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])
    
    def get_cover_url(self):
        cover = None
        cover_url = os.path.join("/static", "books", "generic_book_cover.jpg")
        try:
            if not self.cover_url and not self.cover:
                self._set_cover_url()
                self._set_cover()
            elif self.cover_url and not self.cover:
                self._set_cover()
            if self.cover:
                cover_url = self.cover.url
            else:
                raise Exception("unable to get final image of saved cover.url !")
            logger.info(f"get_cover_url - {cover_url}")
        except Exception as e:
            logger.error(f"get_cover_url | {self} | {e} | {cover_url}")
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
            logging.error(f"{e}: temp_book_file_link is not an allowable book file type... {temp_book_file_link}")

        except Exception as e:
            # attempt removal in case of error
            os_silent_remove(new_file_path)

            # debug
            error_log += f"self BOOK @@@!!!: {self}"
            error_log += f"new_file_path: {new_file_path}"
            error_log += f"json_links: {self.json_links}"
            error_log += f"temp_book_file_link: {temp_book_file_link}"
            error_log += f"temp_book_file_dl: {temp_book_file_dl}"
            error_log += f"langauge: {language}"
            logging.error(f"{e}: {error_log}")
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
        # get book file path
        book_file_path = self.get_book_file_path(language)

        # set template message (appropriate recipients)
        template_message = copy.deepcopy(EMAIL_TEMPLATE_LIST)
        template_message[3] = emails

        # send - return status
        status = send_emails(template_message, [book_file_path])
        return status

    @classmethod
    def search(cls, query):
        """checks db first to see if we may already have a record (bypass api query)"""
        books = None
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
            search_query = reduce(lambda x, y: x | y, search_terms)
            exact_match_query = reduce(lambda x, y: x | y, exact_match)

            # add a field that denotes an exact match
            books = cls.objects.annotate(
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