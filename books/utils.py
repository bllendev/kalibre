import os
import copy
from libgen_api import LibgenSearch


class LibgenBook:
    BOOK_TEMPLATE = {
        'title': '',
        'author': '',
        'file_type': '',
        'links': '',
    }

    def __init__(self, book_api):
        self.book = self._load_book_api(book_api)
        self.author = self.book['author']
        self.title = self.book['title']
        self.file_type = self.book['file_type']
        self.links = self.book['links']

    def _load_book_api(self, book_api):
        book_dict = copy.deepcopy(self.BOOK_TEMPLATE)
        book_dict['author'] = book_api['Author']
        book_dict['title'] = book_api['Title']
        book_dict['file_type'] = book_api['Extension']
        book_dict['links'] = [book_api['Mirror_1'], book_api['Mirror_2'], book_api['Mirror_3']]
        return book_dict


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

    def __init__(self, title_search):
        self.libgen = LibgenSearch()
        self.title_search = title_search
        # self.title_first_choice = self.get_title_choices()[0]

    def get_book_list(self):
        book_list = []
        title_choices = self._get_title_choices()
        try:
            book_list = [LibgenBook(title) for title in self._get_title_choices()]
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            return book_list

    def _get_title_choices(self):
        title_filters = {"Extension": "epub"}
        titles = self.libgen.search_title_filtered(self.title_search, title_filters)
        authors = self.libgen.search_author_filtered(self.title_search, title_filters)
        # titles = self.libgen.search_title(self.title_search)
        # authors = self.libgen.search_authors(self.title_search)
        return titles + authors

    def get_title_download_link(self, title):
        download_links = self.libgen.resolve_download_links(title)
        return download_links

    def get_first_download_link(self):
        try:
            first = self._get_title_choices()[0]
        except Exception as e:
            print(f"ERROR: {e}")
            print(f"self._get_title_choices(): {self._get_title_choices()}")
        return self.get_title_download_link(first)

    def download_book(self):
        pass
