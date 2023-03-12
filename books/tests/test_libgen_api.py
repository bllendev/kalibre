from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
import factory
import requests

from django.conf import settings

from books.libgen_api import LibgenSearch, SearchRequest

from bs4 import BeautifulSoup
import json

"""
    - HOW TO RUN TESTS:
    - ... $ docker compose exec web python manage.py test --noinput --parallel
"""


class TestLibgenSearch:

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    def setUp(self):
        self.libgen_search = LibgenSearch()
        self.test_query = "harry potter"
        self.libgen_book = None

        # open the file for reading in binary mode
        with open(os.path.join(settings.BASE_DIR, "books", "tests", "pkl", "test_hp_book.pkl", "rb")) as pkl:
            # unpickle the list object from the file
            self.test_results = pickle.load(pkl)

    def test_search_title(self):
        results = self.libgen_search.search_title(self.test_query)
        self.assertTrue(results)
        self.assertEquals(results, self.test_results)

    def test_search_author(self):
        results = self.libgen_search.search_author(self.test_query)
        self.assertTrue(results)

    def test_resolve_download_links(self):
        results = self.libgen_search.resolve_download_links(self.libgen_book)
        self.assertTrue(results)



class TestSearchRequest:
    """
        - USAGE: req = search_request.SearchRequest("[QUERY]", search_type="[title]")
    """

    TEST_COLUMNS = [
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

    TEST_LIBGEN_MIRRORS = [
        "https://libgen.is",
        "http://libgen.gs",
        "http://gen.lib.rus.ec",
        "http://libgen.rs",
        "https://libgen.st",
        "https://libgen.li",
    ]

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False

    def setUp(self):
        self.test_search_request = SearchRequest("harry potter")
    
    def test_constants(self):
        self.assertEqual(self.test_search_request.COLUMNS, self.TEST_COLUMNS)
        self.assertEqual(self.test_search_request.LIBGEN_MIRRORS, self.TEST_LIBGEN_MIRRORS)

    def test_strip_i_tag_from_soup(self):
        pass

    def test_get_search_url(self):
        pass

    def test_get_search_page(self):
        pass
    
    def test_aggregate_request_data(self):
        pass



# make a TestLibgenAPI class that inherits from TestCase and has a setUp method and tests that pertain to the LibgenAPI class

class TestLibgenAPI(TestCase):

    _multiprocess_can_split_ = True
    _multiprocess_shared_ = False
    
    def setUp(self):
        self.test_user = 
