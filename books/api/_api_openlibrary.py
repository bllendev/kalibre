import requests
from bookstore_project.logging import log
import logging


logger = logging.getLogger(__name__)


class OpenLibraryAPI:

    BASE_URL = "https://openlibrary.org/"
    SEARCH_URL = f"{BASE_URL}search.json"
    AUTHOR_URL = f"{BASE_URL}authors/"  # /Oid.json

    def __init__(self):
        pass

    def _get_book_search_results(self, query):
        params = {"q": query}
        response = requests.get(self.SEARCH_URL, params=params)
        
        # It's better to check the response status code
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @log
    def get_book_search_results(self, query):
        book_search_results = None
        try:
            _book_search_results = self._get_book_search_results(query)
            book_search_results = _book_search_results["docs"]
        except Exception as e:
            logger.error(f"{e}")
            raise e
        return book_search_results

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
            logger.error(e)
            raise e

        return author