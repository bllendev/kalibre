# import requests

# from gutenberg import GutenbergAPI
# from gutenberg.models import Book
# from gutenberg.exceptions import APIException


# class GutenbergAPI(GutenbergAPI):
#     def __init__(self, search=None, instance_url="https://gutendex.com"):
#         super().__init__(instance_url)

#     def __get_books(
#         self,
#         author_year_start: int = None,
#         author_year_end: int = None,
#         copyright: str = None,
#         ids: list[int] = None,
#         languages: list[str] = None,
#         mime_type: str = None,
#         search: str = None,
#         sort: str = None,
#         topic: str = None,
#         # Add your custom parameters here
#         custom_param_1=None,
#         custom_param_2=None,
#     ):
#         endpoint = self.instance_url + "/books"
#         response = requests.get(
#             endpoint,
#             params={
#                 "author_year_start": author_year_start,
#                 "author_year_end": author_year_end,
#                 "copyright": copyright,
#                 "ids": ids,
#                 "languages": languages,
#                 "mime_type": mime_type,
#                 "search": search,
#                 "sort": sort,
#                 "topic": topic,
#                 # Add your custom parameters to the request
#                 "custom_param_1": custom_param_1,
#                 "custom_param_2": custom_param_2,
#             },
#             timeout=30,
#         )
#         response.raise_for_status()
#         response = response.json()
#         if response.get("detail"):
#             raise APIException(str(response["detail"]))
#         return [Book.from_json(book_json) for book_json in response["results"]]

#     def get_unique_book_list(self, search=None, **kwargs):
#         search = search if search else self.search
#         if not search:
#             raise APIException("No search term provided.")
#         return self.__get_books(search=search, **kwargs)
