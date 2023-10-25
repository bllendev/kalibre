import json

from books.utils import process_text
from books.api._api_openlibrary import OpenLibraryAPI
        

import logging
logger = logging.getLogger(__name__)


openlibrary_api = OpenLibraryAPI()


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
        openlibrary_books = openlibrary_api.get_book_search_results(search_query)
        openlibrary_book_set = {cls(**book) for book in openlibrary_books}
        # libgen_book_set = {APIBook(**book) for book in self.libgen_api.get_book_search_results(self.search_query)}
        return openlibrary_book_set

    def __iter__(self):
        return iter(self.__dict__.items())

    def __next__(self):
        raise StopIteration()

    def __hash__(self):
        """Return a unique hash value based on book's title and ISBN."""
        return hash((self.title, self.isbn))

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
        return self.title == other.title and self.author == other.author

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
