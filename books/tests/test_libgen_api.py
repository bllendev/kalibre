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

    def setUp(self):
        self.libgen_search = LibgenSearch()
        self.test_query = "harry potter"
        self.libgen_book = None

        self.results = self.libgen_search.search_title(self.test_query)



    def test_search_title(self):
        results = self.libgen_search.search_title(self.test_query)
        self.assertTrue(results)

    def test_search_author(self):
        results = self.libgen_search.search_author(self.test_query)
        self.assertTrue(results)

    def test_resolve_download_links(self):
        results = self.libgen_search.resolve_download_links(self.libgen_book)
        self.assertTrue(results)



# def test_filter_results(results, filters, exact_match):
#     """
#     Returns a list of results that match the given filter criteria.
#     When exact_match = true, we only include results that exactly match
#     the filters (ie. the filters are an exact subset of the result).

#     When exact-match = false,
#     we run a case-insensitive check between each filter field and each result.

#     exact_match defaults to TRUE -
#     this is to maintain consistency with older versions of this library.
#     """

#     filtered_list = []
#     if exact_match:
#         for result in results:
#             if filters.items() <= result.items():  # check whether a candidate result matches the given filters
#                 filtered_list.append(result)

#     else:
#         filter_matches_result = False
#         for result in results:
#             for field, query in filters.items():
#                 if query.casefold() in result[field].casefold():
#                     filter_matches_result = True
#                 else:
#                     filter_matches_result = False
#                     break
#             if filter_matches_result:
#                 filtered_list.append(result)
#     return filtered_list


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
    
    def setUp(self):
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test_em
