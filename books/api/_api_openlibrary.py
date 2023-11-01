import requests
from bookstore_project.logging import log
import logging


logger = logging.getLogger(__name__)


class OpenLibraryAPI:

    BASE_URL = "https://openlibrary.org/"
    SEARCH_URL = f"{BASE_URL}search.json"
    AUTHOR_URL = f"{BASE_URL}authors/"  # /Oid.json
    KEY_DICT = {
        "key": "isbn",
        "author_name": "author",  # author_key for id
        "title": "title",
        "cover_i": "cover_url",
    }

    def __init__(self):
        pass

    def _get_book_search_results(self, query):
        params = {"q": query}
        response = requests.get(self.SEARCH_URL, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @log
    def get_book_search_results(self, query):
        book_search_results = None
        try:
            _book_search_results = self._get_book_search_results(query)
            book_search_results = [book for book in _book_search_results["docs"]]
        except Exception as e:
            logger.error(f"get_book_search_results - {e}")
            raise e
        return book_search_results

    def get_book(self, book_id):
        # key implies we are using works/oid
        if "key" in self.KEY_DICT:
            response = requests.get(f"self.{BASE_URL}/works/{book_id}.json")
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

    @log
    def get_author(self, author_id):
        author = ""
        try:
            # url get author by api
            response = requests.get(f"{self.AUTHOR_URL}{author_id}.json")
            
            # It's better to check the response status code
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

        except Exception as e:
            logger.error(f"get_author - {e}")
            raise e

        return author

    @staticmethod
    def get_cover_url(cover_id, size="M"):
        """gets cover url for openlibrary link to cover of book
        - param size: "S", "M", "L"
        """
        cover_id = str(cover_id)  # force cast str
        if size not in ["S", "M", "L"]:
            raise NotImplementedError("get_cover_url - must have a size of the following choices ... S, M, L | you had size: {size}")
        if "OL" in cover_id:
            return f"https://covers.openlibrary.org/b/olid/{cover_id.split('works/')[1]}-{size}.jpg"
        else:
            return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"
