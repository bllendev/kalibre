import json
from rapidfuzz import fuzz
import string

from books.utils import process_text
from books.api._api_openlibrary import OpenLibraryAPI
from books.api._api_libgen import LibgenAPI

import logging

logger = logging.getLogger(__name__)

openlibrary_api = OpenLibraryAPI()
libgen_api = LibgenAPI()


def normalize_text(text):
    """Normalize the text for better comparison."""
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip().replace("-", " ")

def book_match_bln(book, other_book):
    normalized_title = normalize_text(book['title'])
    normalized_author = normalize_text(book['author'])
    normalized_title_other = normalize_text(other_book['title'])
    normalized_author_other = normalize_text(other_book['author'])
    # Compare titles
    title_similarity = fuzz.ratio(normalized_title, normalized_title_other)

    # Compare authors
    author_similarity = fuzz.ratio(normalized_author, normalized_author_other)

    if title_similarity > 80 and author_similarity > 40:
        return True
    elif title_similarity >= 90:
        return True

    # print(f"normalized_title: {normalized_title}")
    # print(f"normalized_author: {normalized_author}")
    # print(f"normalized_title_other: {normalized_title_other}")
    # print(f"normalized_author_other: {normalized_author_other}")

    # print(f"title_similarity: {title_similarity}")
    # print(f"author_similarity: {author_similarity}")
    # print(F"---------------------------")
    return False

def find_matching_books(book, libgen_books, filetype):
    for libgen_book in libgen_books:
        if libgen_book["filetype"] == filetype:
            if book_match_bln(book, libgen_book):
                return libgen_book

    return None


class APIBook:
    """
    Represents a book fetched from an API.

    Attributes:
        isbn (str): The ISBN of the book.
        author (str): The author of the book.
        title (str): The title of the book.
        filetype (str): The file extension/type of the book.
        json_links (str): JSON serialized string containing download mirror links.
        _title_lemmatized (str): Processed and lemmatized title for advanced search.

    Constants:
        LIBGEN_KEY_DICT (dict): Mapping of LibGen API response keys to `APIBook` attributes.
        OPENLIBRARY_KEY_DICT (dict): Mapping of OpenLibrary API response keys to `APIBook` attributes.
    """

    LIBGEN_KEY_DICT = {
        "ID": "isbn",
        "Author": "author",
        "Title": "title",
        "Extension": "filetype",
    }

    OPENLIBRARY_KEY_DICT = {
        "key": "isbn",
        "author_name": "author",  # author_key for id
        "title": "title",
    }

    def __init__(self, **kwargs):
        """
        Initialize an instance of `APIBook` using API response data.

        Args:
            **kwargs: Arbitrary keyword arguments containing API response data.
        """
        # Initializing default attributes
        self.isbn = ""
        self.author = ""
        self.title = ""
        self.filetype = ""
        self.json_links = ""
        self._title_lemmatized = ""

        for original_key, v in kwargs.items():
            # catch and prepare all libgen data
            libgen_key = self.LIBGEN_KEY_DICT.get(original_key)
            if libgen_key:
                setattr(self, libgen_key, str(v).replace("&amp", ""))

            # catch and prepare all openlibrary data
            openlibrary_key = self.OPENLIBRARY_KEY_DICT.get(original_key)
            if openlibrary_key:
                # prepare author data
                if original_key == "author_name":  # TODO: want this to save author and id and leverage db overtime
                    author_list = list(v)
                    v = author_list[0]
                    # author_dict = openlibrary_api.get_author(author_list[0])  if id
                    # v = author_dict["name"]

                setattr(self, openlibrary_key, str(v))


        # get links
        try:
            self.json_links = json.dumps([
                kwargs['Mirror_1'],
                kwargs['Mirror_2'],
                kwargs['Mirror_3'],
            ])
        except KeyError as e:
            logger.error(f"OpenLibraryAPI does not have Mirror_* fields")
            self.filetype = ""

        try:
            # set lemmatized title
            self._title_lemmatized = process_text(self.title)
        except KeyError as e:
            logger.error(f"OpenLibraryAPI does not have title ?")
            logger.error(f"Values: {self.__dict__}")
            raise e

    @classmethod
    def __call__(cls, search_query):
        """
        Fetch books based on a search query from OpenLibrary API.

        Args:
            search_query (str): The search term to find books.

        Returns:
            set: A set of `APIBook` instances representing the books found.
        """
        # openlibrary api
        openlibrary_books = openlibrary_api.get_book_search_results(search_query)
        openlibrary_book_set = {cls(**book) for book in openlibrary_books}

        # libgen api
        libgen_books = libgen_api.get_book_search_results(search_query)
        libgen_book_set = {cls(**book) for book in libgen_books}

        # get final output
        output_list = list()
        for book in openlibrary_book_set:
            epub_match = find_matching_books(book, libgen_book_set, "epub")

            if epub_match:
                book.json_links = epub_match.json_links
                book.filetype = epub_match.filetype

            output_list.append(book)
        
        return set(output_list)

    def __iter__(self):
        return iter(self.__dict__.items())

    def __next__(self):
        raise StopIteration()

    def __hash__(self):
        """Return a unique hash value based on book's title."""
        return hash(normalize_text(self.title))

    def __eq__(self, other):
        """
        Determine equality based on book's title and author.

        Args:
            other (APIBook): Another `APIBook` instance.

        Returns:
            bool: True if both books have the same title and author, otherwise False.
        """
        if not isinstance(other, APIBook):
            return NotImplemented

        return book_match_bln(self, other)

    def __getitem__(self, item):
        """
        Allows dictionary-like access to `APIBook` attributes.

        Args:
            item (str): The attribute name.

        Returns:
            any: The value of the specified attribute.
        """
        return getattr(self, item)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)
