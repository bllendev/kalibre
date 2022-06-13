import os
from libgen_api import LibgenSearch


class LibgenAPI:

    def __init__(self, title_search):
        self.libgen = LibgenSearch()
        self.title_search = title_search
        # self.title_first_choice = self.get_title_choices()[0]

    def get_title_choices(self):
        title_filters = {"Extension": "mobi"}
        titles = self.libgen.search_title_filtered(self.title_search, title_filters, exact_match=False)
        return titles

    def get_title_download_link(self, title):
        download_links = self.libgen.resolve_download_links(title)
        return download_links

    def get_first_download_link(self):
        try:
            first = self.get_title_choices()[0]
        except Exception as e:
            print(f"ERROR: {e}")
            print(f"self.get_title_choices(): {self.get_title_choices()}")
        return self.get_title_download_link(first)

    def download_book(self):
        pass
