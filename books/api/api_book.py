import json
from rapidfuzz import fuzz
import string

from books.utils import process_text
from books.api._api_openlibrary import OpenLibraryAPI
from books.api._api_libgen import LibgenAPI

import logging
logger = logging.getLogger(__name__)


def normalize_text(text):
    """Normalize the text for better comparison."""
    return text.lower().translate(str.maketrans('', '', string.punctuation + "- ")).strip()

def book_match_bln(book, other_book):
    normalized_title = normalize_text(book['title'])
    normalized_author = normalize_text(book['author'])
    normalized_title_other = normalize_text(other_book['title'])
    normalized_author_other = normalize_text(other_book['author'])
    # Compare titles
    title_similarity = fuzz.ratio(normalized_title, normalized_title_other)

    # Compare authors
    author_similarity = fuzz.ratio(normalized_author, normalized_author_other)

    if title_similarity > 70 and author_similarity > 42:
        return True

    elif title_similarity >= 85:
        return True

    # print(f"normalized_title: {normalized_title}")
    # print(f"normalized_author: {normalized_author}")
    # print(f"normalized_title_other: {normalized_title_other}")
    # print(f"normalized_author_other: {normalized_author_other}")

    # print(f"title_similarity: {title_similarity}")
    # print(f"author_similarity: {author_similarity}")
    # print(F"---------------------------")
    return False

def find_matching_books(book, other_books, filetype):
    for other_book in other_books:
        if other_book["filetype"] == filetype:
            if book_match_bln(book, other_book):
                return other_book
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
    OPENLIBRARY_KEY_DICT = OpenLibraryAPI.KEY_DICT
    LIBGEN_KEY_DICT = LibgenAPI.KEY_DICT

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
        self.cover_url = ""
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

                if original_key == "cover_i":
                    v = OpenLibraryAPI.get_cover_url(cover_id=v, size="L")

                if original_key == "isbn":
                    isbn_list = list(v)
                    v = isbn_list[0]
                setattr(self, openlibrary_key, str(v))


        # get links
        try:
            self.json_links = json.dumps([
                kwargs['Mirror_1'],
                kwargs['Mirror_2'],
                kwargs['Mirror_3'],
            ])
        except KeyError as e:
            logger.info(f"OpenLibraryAPI does not have Mirror_* fields")
            self.filetype = ""

        self._title_lemmatized = process_text(self.title)

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

        if book_match_bln(self, other):
            return True

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
