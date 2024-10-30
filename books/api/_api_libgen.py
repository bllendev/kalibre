# tools
import requests

import collections
collections.Callable = collections.abc.Callable

from bs4 import BeautifulSoup
from itertools import chain
from django.core.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)


MIRROR_SOURCES = ["GET", "Cloudflare", "IPFS.io", "Infura"]


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

    KEY_DICT = {
        "ID": "isbn",
        "Author": "author",
        "Title": "title",
        "Extension": "filetype",
    }

    STABLE_FILE_TYPES = {"epub", "mobi"}

    def __init__(self):
        self.libgen = LibgenSearch()

    def fetch_books(self, query):
        book_search_results = list()
        try:
            titles = self.libgen.search_title(query)
            authors = self.libgen.search_author(query)
            book_search_results = [api_book for api_book in chain(titles, authors)]  # chains iterables' elements into single iterable
        except Exception as e:
            logger.error(f"_api_libgen | {e}")
        return book_search_results


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
        if len(self.query) < 3:
            raise ValidationError("Error when searching for your request, the Query was too short")

        self.query = query
        self.search_type = search_type.lower()
  

    def aggregate_request_data(self):
        query_parsed = "%20".join(self.query.split(" "))
        search_page = None

        i = 0  # parse until real mirror is found or until we run out of mirrors !
        while (search_page is None or search_page.status_code != 200) and i < len(self.LIBGEN_MIRRORS):
            libgen_mirror = self.LIBGEN_MIRRORS[i]
            search_type_url = f"{libgen_mirror}/search.php?req={query_parsed}&column={self.search_type}"
            search_url = self.get_search_url(libgen_mirror, query_parsed)
            search_page = requests.get(search_url)
            i += 1
        
        # validate search_page
        if not search_page:
            raise RuntimeError("No search page found for libgen link")

        # bs4 !
        soup = BeautifulSoup(search_page.text, "lxml")

        # strip i tags from soup
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

        # Libgen results contain 3 tables
        # Table2: Table of data to scrape.
        information_table = []
        try:
            information_table = soup.find_all("table")[2]
        except Exception as e:
            logger.debug(f"SearchRequest.aggregate_request_data: {e}")
            logger.debug(soup)

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

