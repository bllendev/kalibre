# tools
import requests
from bs4 import BeautifulSoup
from functools import reduce
import json
from collections import defaultdict
import jellyfish

# import nltk
# from nltk.stem import PorterStemmer
# from ebooklib import epub

# django
from django.conf import settings
from django.db.models import Q

# local
from users.models import Email
from books.models import Book
from books.utils import (
    bulk_save,
    os_silent_remove,
    process_text,
)


MIRROR_SOURCES = ["GET", "Cloudflare", "IPFS.io", "Infura"]


class LibgenBook:
    """
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

    def __init__(self, **kwargs):
        self.values = {}

        # get values (normalize)
        for k, v in kwargs.items():
            k = self.LIBGEN_KEY_DICT.get(k)
            if k:
                k = str(k).strip().replace("/", "-").replace(" ", "_")
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
        print(f"self.values['_title_lemmatized']: {self.values['_title_lemmatized']}")

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

    STABLE_FILE_TYPES = {"epub", "mobi"}

    def __init__(self, title_search=None, force_api=False):
        self.libgen = LibgenSearch()
        self.search_query = title_search
        self.force_api = force_api
        # self._dev_debug()

    def _dev_debug(self):
        pass

    def _book_db_search(self):
        """checks db first to see if we may already have a record (bypass api query)"""
        search_terms = [
            Q(title__icontains=self.search_query),
            Q(author__icontains=self.search_query),
            Q(filetype__icontains=self.search_query),
            Q(isbn__icontains=self.search_query),
            Q(title__icontains=self.search_query.strip()),
            Q(author__icontains=self.search_query.strip()),
            Q(filetype__icontains=self.search_query.strip()),
            Q(isbn__icontains=self.search_query.strip()),
            Q(_title_lemmatized__icontains=self.search_query.replace(" ", "")),
            Q(_title_lemmatized__icontains=self.search_query.strip()),
        ]

        # combine the search terms with OR operator
        search_query = reduce(lambda x, y: x | y, search_terms)

        # return query the database to get matching books
        return Book.objects.filter(search_query)

    def _get_libgen_book_list(self):
        try:
            # get libgen book list
            titles = self.libgen.search_title(self.search_query)
            authors = self.libgen.search_author(self.search_query)
            _libgen_book_list = [LibgenBook(**api_book) for api_book in titles + authors]

            # filter list of LibgenBooks by stable files for now (epub, mobi)
            libgen_book_list = [book for book in _libgen_book_list if book.filetype in self.STABLE_FILE_TYPES]

        except Exception as e:
            print(f"ERROR | _get_libgen_book_list | {e}")
            libgen_book_list = []

        finally:
            return libgen_book_list

    def is_duplicate(book1, book2, title_similarity_threshold=0.88):
        if not book1 or book2:
            return False

        title_similarity = jellyfish.jaro_winkler(book1._title_lemmatized, book2._title_lemmatized)
        if title_similarity >= title_similarity_threshold:
            return True

        return False

    def filter_duplicates(self, book_list):
        unique_books = []

        for book in book_list:
            duplicate_found = False
            for unique_book in unique_books:
                if self.is_duplicate(book, unique_book):
                    duplicate_found = True
                    continue

            if not duplicate_found:
                unique_books.append(book)

        return unique_books

    def get_unique_book_list(self):
        # check books in db first
        db_books = self._book_db_search()

        print(F"BOOKS: {db_books}")
        print(F"self.search_query: {self.search_query}")

        # if not reasonable selection, do fresh query using libgen api
        if not db_books or self.force_api:
            api_books = self._get_libgen_book_list()
            filter_api_books = self.filter_duplicates(api_books)

            print(f"filter_api_books: {filter_api_books}")

            to_save_books = []
            for api_book in filter_api_books:
                # Check if the api_book is a duplicate of any existing book in db_books
                duplicate_found = any(self.is_duplicate(api_book, db_book) for db_book in db_books)

                # Add the book to the list of books to save only if it is not a duplicate
                if not duplicate_found:
                    to_save_books.append(Book(**api_book.values))

            bulk_save(to_save_books)

            db_books = list(db_books) + to_save_books

        return db_books

    def get_book(self, isbn, book_title, filetype):
        # get book record from db!
        new_book = Book.objects.filter(isbn__icontains=isbn, filetype=filetype).first()          # THESE ISBN SHOULD BE ALL UNIQUE RIGHT ??? @AG++
        if not new_book:
            new_book = Book.objects.filter(title__icontains=book_title, filetype=filetype).first()
        return new_book


class LibgenSearch:
    def search_title(self, query):
        search_request = SearchRequest(query, search_type="title")
        return search_request.aggregate_request_data()

    def search_author(self, query):
        search_request = SearchRequest(query, search_type="author")
        return search_request.aggregate_request_data()

    def resolve_download_links(self, item):
        mirror_1 = item["Mirror_1"]
        page = requests.get(mirror_1)
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all("a", string=MIRROR_SOURCES)
        download_links = {link.string: link["href"] for link in links}
        return download_links

# ----------------------------------------------------- #


class SearchRequest:
    """
        - USAGE: req = search_request.SearchRequest("[QUERY]", search_type="[title]")
    """

    COLUMNS = [
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

    LIBGEN_MIRRORS = [
        "https://libgen.is",
        "http://libgen.gs",
        "http://gen.lib.rus.ec",
        "http://libgen.rs",
        "https://libgen.st",
        "https://libgen.li",
    ]

    def __init__(self, query, search_type="title"):
        self.query = query
        self.search_type = search_type.lower()

        if len(self.query) < 3:
            raise Exception("Query is too short")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_url(self, libgen_mirror, query_parsed):
        SEARCH_TYPE_URL_DICT = {
            "title": f"{libgen_mirror}/search.php?req={query_parsed}&column=title",
            "author": f"{libgen_mirror}/search.php?req={query_parsed}&column=author",
        }
        return SEARCH_TYPE_URL_DICT[self.search_type]

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
        search_page = None

        i = 0       # parse until real mirror is found or until we run out of mirrors !
        while (search_page is None or search_page.status_code != 200) and i < len(self.LIBGEN_MIRRORS):
            libgen_mirror = self.LIBGEN_MIRRORS[i]
            search_url = self.get_search_url(libgen_mirror, query_parsed)
            search_page = requests.get(search_url)

            i += 1

        return search_page

    def aggregate_request_data(self):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "lxml")
        self.strip_i_tag_from_soup(soup)

        # Libgen results contain 3 tables
        # Table2: Table of data to scrape.
        information_table = []
        try:
            information_table = soup.find_all("table")[2]
        except Exception as e:
            print(F"libgen_api.aggregate_request_data: {e}")
            print(soup)

        # Determines whether the link url (for the mirror)
        # or link text (for the title) should be preserved.
        # Both the book title and mirror links have a "title" attribute,
        # but only the mirror links have it filled.(title vs title="libgen.io")
        raw_data = [
            [
                td.a["href"]
                if td.find("a")
                and td.find("a").has_attr("title")
                and td.find("a")["title"] != ""
                else "".join(td.stripped_strings)
                for td in row.find_all("td")
            ]
            for row in information_table.find_all("tr")[
                1:
            ]  # Skip row 0 as it is the headings row
        ]

        output_data = [dict(zip(self.COLUMNS, row)) for row in raw_data]
        return output_data

