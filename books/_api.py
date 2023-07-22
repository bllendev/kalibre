# django
from django.db.models import Q
from django.db.models import Case, When
from django.db import models
from functools import reduce
import json

from books.api_libgen import LibgenAPI
# from books.api_gutenberg import GutenbergAPI
from books.models import Book
from books.utils import process_text


class APIBook:
    """
    - used by BookAPI class
    - a handy class that streamlines our scraped
    libgen api books into a nice accessible class
    for our Book model
    """
    LIBGEN_KEY_DICT = {
        "ID": "isbn",
        "Author": "author",
        "Title": "title",
        "Extension": "filetype",
    }

    API_LIST = [
        "libgen",
        "gutenberg",
    ]

    def __init__(self, **kwargs):
        self.values = {}

        # get values (normalize)
        for k, v in kwargs.items():
            k = self.LIBGEN_KEY_DICT.get(k)
            if k:
                k = str(k).strip().replace("/", "-").replace(" ", "_")
                v = str(v).replace("&amp", "")
                self.values.update({k: v})

        # get links
        self.values.update({
            "json_links": json.dumps([
                kwargs['Mirror_1'],
                kwargs['Mirror_2'],
                kwargs['Mirror_3'],
            ]),
        })

        # get lemmatized title
        self.values.update({
            "_title_lemmatized": process_text(self.values["title"])
        })

    def __iter__(self):
        return iter(self.values.items())

    def __next__(self):
        raise StopIteration()

    def __getattr__(self, key):
        try:
            return self.values[key]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        if key == 'values':
            super().__setattr__(key, value)
        else:
            self.values[key] = value

    def __hash__(self):
        return hash((self.values['title'], self.values['author']))

    def __eq__(self, other):
        if not isinstance(other, APIBook):
            return NotImplemented
        return self.values['title'] == other.values['title'] and self.values['author'] == other.values['author']


class BookAPI:
    """
    - handles all Book API calls, normalizing books from different sources
    and removing potential duplicates.
    - also handles the creation of new books and pulling from the database
    """

    def __init__(self, search_query=None, force_api=False):
        self.force_api = force_api
        self.search_query = search_query
        self.db_books = self._book_db_search()
        self.libgen_api = LibgenAPI(search_query)
        # self.gutenberg_api = GutenbergAPI(search_query)

    def _book_db_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        books = None
        if self.search_query:
            self.search_query = self.search_query.strip()
            search_terms_list = self.search_query.split()

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
            books = Book.objects.annotate(
                is_exact_match=Case(
                    When(exact_match_query, then=1),
                    default=0,
                    output_field=models.IntegerField()
                ),
                title_match=Case(
                    When(Q(title__icontains=self.search_query), then=1),
                    default=0,
                    output_field=models.IntegerField(),
                ),
                author_match=Case(
                    When(Q(author__icontains=self.search_query), then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ).filter(search_query)

            # order by the new field, so exact matches and then title matches and then author matches come first
            books = books.order_by('-is_exact_match', '-title_match', '-author_match')

        # return query the database to get matching books
        return books

    def get_unique_book_list(self):
        db_books = set(self.db_books)
        if len(db_books) < 3 or self.force_api:
            libgen_book_set = {APIBook(**book) for book in self.libgen_api.get_unique_book_list()}
            db_books.update(libgen_book_set)

        # create list of unique books to be created in the db
        books_to_create = []
        for book in db_books:
            # check if book already exists in db
            if not Book.objects.filter(isbn=book.isbn).exists():
                books_to_create.append(Book(**book.values))

        # bulk create new books
        Book.objects.bulk_create(books_to_create)
        # Book.objects.create_and_embed_books(**book_info)

        return self._book_db_search()

    def get_book(self, isbn, book_title, filetype):
        """
        gets the intended book from the database
        """
        new_book = Book.objects.filter(isbn__icontains=isbn, filetype=filetype).first()  # THESE ISBN SHOULD BE ALL UNIQUE RIGHT ??? @AG++
        if not new_book:
            new_book = Book.objects.filter(title__icontains=book_title, filetype=filetype).first()
        return new_book
