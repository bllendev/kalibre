import requests
import logging

logger = logging.getLogger(__name__)


def create_or_get_book_from_api(api_book):
    """
    Create or get a Book instance from an API response dictionary.

    Args:
        api_book (dict): API response containing book data.

    Returns:
        Book: Created or existing Book instance.
        created: bool
    """
    from books.models import Book
    from authors.models import Author
    from django.db import transaction

    collected_authors = []

    with transaction.atomic():
        # extract relevant details from the API response
        title = api_book.get("title", "")
        isbns = api_book.get("isbn", [])
        work_key = api_book.get("key", "")
        cover_id = api_book.get("cover_i", "")
        cover_url = "http://covers.openlibrary.org/b/id/"
        cover_url += f"{cover_id}-L.jpg" if cover_id else ""
        # NOTE: publish_dates can be a bigass list of all publication and not 1-1 with rest of data, just not gonna worry about it.
        # publish_dates = api_book.get("publish_date", [])
        # publish_date = ", ".join(publish_dates)
        subjects = api_book.get("subject", [])

        # handle authors
        author_keys = api_book.get("author_key", [])
        author_names = api_book.get("author_name", [])
        for author_key, author_name in zip(author_keys, author_names):
            author, _ = Author.objects.get_or_create(
                key=author_key,
                defaults={
                    "name": author_name,
                    "alternative_names": [],
                },
            )
            collected_authors.append(author)

        # get or create the book instance
        book, created = Book.objects.get_or_create(
            key=work_key,
            defaults={
                "title": title,
                "isbns": isbns,
                "cover_url": cover_url,
                # "publish_date": publish_date,
                "subjects": subjects,
                "json": api_book,
            },
        )

        if created:
            # Linked authors need to be set only for newly created books
            book.authors.set(collected_authors)

    return book, created


class OpenLibraryAPI:
    """
    TODO: consider decomping into functions...
    - fetch: query of some book, author, (maybe publisher)
    - get: query of individual book, author, (maybe publisher)
    """

    BASE_URL = "https://openlibrary.org/"
    SEARCH_URL = f"{BASE_URL}search.json"
    AUTHOR_URL = f"{BASE_URL}authors/"  # /Oid.json
    COVER_URL = "https://covers.openlibrary.org/b"

    def __init__(self):
        pass

    def fetch_books(self, query):
        try:
            book_search_results = None
            params = {"q": query}
            response = requests.get(self.SEARCH_URL, params=params)
            response.raise_for_status()
            book_search_results = response.json()  # example here:
            book_search_results = [b for b in book_search_results["docs"]]
            logger.info(
                f"""
                openlibrary api fetch_books query made...
                {len(book_search_results)} books found
                """
            )
            return book_search_results
        except Exception as e:
            logger.error(f"Error fetching books from OpenLibraryAPI: {e}")
            logger.exception(e)
            return list()

    def fetch_authors(self, query):
        pass

    def get_book(self, book_id):
        """example here.
        https://openlibrary.org/works/OL45804W.json
        """
        # key implies wmgrepe are using works/oid
        response = requests.get(f"{self.BASE_URL}/{book_id}.json")
        response.raise_for_status()
        return response.json()

    def get_author(self, author_id):
        """
        {
           numFound: 1,
           start: 0,
           numFoundExact: true,
           docs: [
             {
               key: "OL23919A",
               text: [...],
               type: "author",
               name: "J. K. Rowling",
               alternate_names: [...],
               birth_date: "31 July 1965",
               top_work: "Harry Potter and the Philosopher's Stone",
               work_count: 162,
               top_subjects: [...],
               _version_: 1702166143068799000
             },
           ]
         }
        """
        try:
            # url get author by api
            response = requests.get(f"{self.AUTHOR_URL}{author_id}.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"get_author - {e}")
            raise e

    @classmethod
    def get_cover_url(cls, cover_id, size="M"):
        """gets cover url for openlibrary link to cover of book
        - param size: "S", "M", "L"
        """
        # force cast str
        cover_id = str(cover_id)

        # validation
        if size not in ["S", "M", "L"]:
            raise NotImplementedError(
                "get_cover_url - must have a size of the following choices ... S, M, L | you had size: {size}"
            )

        # get url
        url = f"{cls.COVER_URL}/olid/{cover_id.split('works/')[1]}-{size}.jpg"
        if "OL" not in cover_id:
            url = f"{cls.COVER_URL}/id/{cover_id}-{size}.jpg"
        return url
