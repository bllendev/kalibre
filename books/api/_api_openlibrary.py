from bookstore_project.logging import log
import logging

logger = logging.getLogger(__name__)


class OpenLibraryAPI:
    """
    {
        "start": 0,
        "num_found": 629,
        "docs": [
            {...},
            {...},
            ...
            {...}]
    }
    .... s.t each "doc" is...
    {
        "cover_i": 258027,
        "has_fulltext": true,
        "edition_count": 120,
        "title": "The Lord of the Rings",
        "author_name": [
            "J. R. R. Tolkien"
        ],
        "first_publish_year": 1954,
        "key": "OL27448W",
        "ia": [
            "returnofking00tolk_1",
            "lordofrings00tolk_1",
            "lordofrings00tolk_0",
        ],
        "author_key": [
            "OL26320A"
        ],
        "public_scan_b": true
    }

    """
    BASE_URL = "https://openlibrary.org/search.json?"

    def __init__(self):
        pass

    def _get_book_search_results(self):
        pass

    @log
    def get_book_search_results(self):
        try:
            book_list = self._book_search_results()
        except Exception as e:
            logger.error(f"ERROR: books.api._api_openlibrary.get_book_search_results: {e}")
            raise e

    