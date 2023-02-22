import requests
from bs4 import BeautifulSoup

MIRROR_SOURCES = ["GET", "Cloudflare", "IPFS.io", "Infura"]


class LibgenSearch:
    def search_title(self, query):
        search_request = SearchRequest(query, search_type="title")
        return search_request.aggregate_request_data()

    def search_author(self, query):
        search_request = SearchRequest(query, search_type="author")
        return search_request.aggregate_request_data()

    def search_title_filtered(self, query, filters, exact_match=True):
        search_request = SearchRequest(query, search_type="title")
        results = search_request.aggregate_request_data()
        filtered_results = filter_results(results=results, filters=filters, exact_match=exact_match)
        return filtered_results

    def search_author_filtered(self, query, filters, exact_match=True):
        search_request = SearchRequest(query, search_type="author")
        results = search_request.aggregate_request_data()
        filtered_results = filter_results(results=results, filters=filters, exact_match=exact_match)
        return filtered_results

    def resolve_download_links(self, item):
        mirror_1 = item["Mirror_1"]
        page = requests.get(mirror_1)
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all("a", string=MIRROR_SOURCES)
        download_links = {link.string: link["href"] for link in links}
        return download_links


def filter_results(results, filters, exact_match):
    """
    Returns a list of results that match the given filter criteria.
    When exact_match = true, we only include results that exactly match
    the filters (ie. the filters are an exact subset of the result).

    When exact-match = false,
    we run a case-insensitive check between each filter field and each result.

    exact_match defaults to TRUE -
    this is to maintain consistency with older versions of this library.
    """

    filtered_list = []
    if exact_match:
        for result in results:
            if filters.items() <= result.items():  # check whether a candidate result matches the given filters
                filtered_list.append(result)

    else:
        filter_matches_result = False
        for result in results:
            for field, query in filters.items():
                if query.casefold() in result[field].casefold():
                    filter_matches_result = True
                else:
                    filter_matches_result = False
                    break
            if filter_matches_result:
                filtered_list.append(result)
    return filtered_list


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

