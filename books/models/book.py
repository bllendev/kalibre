# django
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.core.files.base import ContentFile
from pgvector.django import L2Distance
import requests

# tools
import uuid
import os

# local
from ai.utils import get_openai_embeddings
from books.api._api_openlibrary import OpenLibraryAPI
from ai.models import VectorSearch

# logs
import logging

logger = logging.getLogger(__name__)


class Book(models.Model):
    """
    Represents a single book, capturing key book metadata
    ... a single record may contain data from several sources such as,
    ... gutenberg
    ... openlibrary
    ... etc
    """

    id = models.UUIDField(
        primary_key=True,
        db_index=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the book instance.",
    )
    # fks
    gutenberg = models.ForeignKey(
        "books.BookGutenberg",
        related_name="books",
        help_text="Link to the related Gutenberg book record.",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    json = models.JSONField(
        default=dict, blank=True, help_text="The original captured data."
    )
    title = models.TextField(
        default="", blank=True, null=False, help_text="The title of the book."
    )
    isbns = models.JSONField(
        blank=True,
        default=list,
        help_text="List of ISBNs",
    )
    key = models.CharField(
        max_length=50,
        blank=True,  # ex: "/works/OL123456W"
        help_text="Key reference to the OpenLibrary work instance.",
    )
    description = models.TextField(
        blank=True, null=True, help_text="A description of the book if provided."
    )
    authors = models.ManyToManyField(
        "authors.Author",
        related_name="books",
        help_text="Authors associated with the book.",
    )
    publish_date = models.CharField(
        max_length=30,
        blank=True,
        help_text="Publication date(s) in a string, formatted as needed.",
    )
    # publishers = models.CharField(
    #     max_length=500, blank=True, help_text="Comma-separated publisher names."
    # )  # TODO: add publishers subapp and model...
    subjects = models.JSONField(
        default=list, blank=True, help_text="List of subjects covered by the book."
    )
    cover_url = models.URLField(blank=True, help_text="URL to the book's cover image.")
    cover = models.ImageField(upload_to="covers/", blank=True)
    vector_search = models.ForeignKey(
        "ai.VectorSearch",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def save_vector(self):
        """
        generate and save a vector embedding for the book using OpenAI's API.

        returns:
            VectorSearch: The associated VectorSearch instance.
        """
        from ai.models import VectorSearch

        authors = [a.name for a in self.authors.all()]
        # publishers = self.publishers.split(", ")  # TODO: build publishers
        input_text = " ".join(
            filter(
                None,
                [
                    f"{self.title}.",
                    f"{self.description}.",
                    f"{', '.join(authors)}",
                    # f"{' and '.join(publishers)}.",
                    f"{', '.join(self.subjects)}.",
                ],
            )
        )

        if not input_text.strip():
            logger.error("Book input text empty, cannot generate embedding.")
            return None

        # generate OpenAI embedding
        try:
            vector = get_openai_embeddings([input_text])
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise e

        # validate vector
        if not vector:
            logger.error(f"""
                            {self}
                            "Title: {self.title}.",
                            "Description: {self.description}.",
                            "Authors: {', '.join(authors)}",
                            "Subjects: {', '.join(self.subjects)}.",
                         """)
            raise RuntimeError("No vector embeddings were extracted")

        # prepare metadata
        metadata = {
            "title": self.title,
            "authors": authors,
            # "publishers": publishers,
            # "publish_date": str(self.publish_date),  # TODO: this field is not wired up
            "subjects": self.subjects,
        }

        # update or create the VectorSearch instance
        if not self.vector_search:
            self.vector_search = VectorSearch.objects.create(
                vector=vector,
                metadata=metadata,
            )
        else:
            self.vector_search.vector = vector
            self.vector_search.metadata = metadata
            self.vector_search.save()

        return self.vector_search

    def save(self, save_vector=False, *args, **kwargs):
        # generate and save vector embeddings
        if save_vector:
            _ = self.save_vector()

        # super save!
        super().save(*args, **kwargs)

    @classmethod
    def search(
        cls,
        query,
        books=None,
        gutenberg=True,  # force only gutenberg books to be included
        top_n=20,
        embeddings=None,
    ):
        """
        search for books based on vector similarity to the query text.

        returns:
            QuerySet: Books matching the similarity criteria.
        """
        if not query:
            raise RuntimeError("no query was entered")

        # generate vector embedding for the query
        # ... (if embeddings not already passed)
        query_vector = embeddings
        if not query_vector:
            query_vector = get_openai_embeddings([query])

        # perform vector similarity search
        similar_vectors = (
            VectorSearch.objects.annotate(
                similarity=L2Distance(F("vector"), query_vector)
            )
            .filter(similarity__lte=5)
            .order_by("similarity")[:top_n]
        )

        logger.debug(f"{len(similar_vectors)} vector")

        # fetch books linked to these vectors
        books = cls.objects.filter(vector_search__in=similar_vectors)

        # gutenberg only?
        if gutenberg:
            books = books.exclude(gutenberg__isnull=True)

        return books

    def _set_cover_url(self):
        """sets the cover_url link in db, used to set the cover images"""
        # setup
        openlibrary_api = OpenLibraryAPI()

        # get data
        openlibrary_book = openlibrary_api.get_book(self.isbns[0])
        cover_id = openlibrary_book["covers"][0]
        cover_url = openlibrary_api.get_cover_url(cover_id)
        if not cover_url:
            raise TypeError("no cover_url was returned !")

        # save to db
        self.cover_url = cover_url
        self.save()
        return cover_url

    def _set_cover(self, cover_url=None):
        """downloads and sets cover image for book from specified URL."""
        cover_url = cover_url if cover_url else self.cover_url
        r = requests.get(cover_url)
        if r.status_code == 200:
            data = r.content
            filename = cover_url.split("/")[-1]
            self.cover.save(filename, ContentFile(data))
            self.save()
        return self.cover

    def get_absolute_url(self):
        """
        returns the URL to access the detail page of this book.
        """
        return reverse("book-detail", args=[str(self.id)])

    def get_cover_url(self, set_cover=False):
        """
        retrieves URL of book's cover image. Sets and saves cover if needed.
        """
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


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    review = models.CharField(max_length=255)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.review
