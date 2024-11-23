from django.test import TestCase
from books.api._api_openlibrary import (
    OpenLibraryAPI,
    create_or_get_book_from_api,
)
from books.tests.constants import (
    TEST_QUERY,
    TEST_QUERY_AUTHOR,
    TEST_AUTHOR_KEY,
)
from authors.factory.author import AuthorFactory
from books.tests.factories import BookFactory

from books.models import Book


"""
docker compose exec web python manage.py test books.tests.test_api_openlibrary --noinput --failfast
"""


class TestOpenLibraryAPI(TestCase):
    def setUp(self):
        self.api = OpenLibraryAPI()
        self.api_response = {
            "title": "My Sweet-orange Tree",
            "isbn": [
                "964913980X",
                "9789649139807",
                "1782692452",
                "1536203289",
                "9781782692454",
                "9781536203288",
            ],
            "key": "/works/OL286593W",
            "cover_i": "10413035",
            "publish_date": ["2019", "Mar 16, 2011"],
            "subject": ["Brazil, fiction", "Children's fiction"],
            "author_key": ["OL2643489A"],
            "author_name": ["Jose Mauro De Vasconcelos"],
        }

    def test_fetch_books(self):
        books = self.api.fetch_books(TEST_QUERY)
        self.assertTrue(books)

    # TODO: implement fetch_authors and test
    # def test_fetch_authors(self):
    #     authors = self.api.fetch_authors(TEST_QUERY_AUTHOR)
    #     self.assertTrue(authors)

    def test_get_author(self):
        author = self.api.get_author(TEST_AUTHOR_KEY)
        self.assertTrue(author)

    def test_create_book_and_author(self):
        # call the function that should create a Book and Author
        book = create_or_get_book_from_api(self.api_response)

        # verify that the Book was created with correct attributes
        self.assertIsInstance(book, Book)
        self.assertEqual(book.title, self.api_response["title"])
        self.assertListEqual(book.isbns, self.api_response["isbn"])
        self.assertTrue(
            book.cover_url.endswith(f"{self.api_response['cover_i']}-L.jpg")
        )
        # self.assertEqual(
        #     book.publish_date, ", ".join(self.api_response["publish_date"])
        # )  # NOTE: publish_date is on hold for now dataset is too big...
        self.assertListEqual(book.subjects, self.api_response["subject"])

        # verify that Author was created and linked
        self.assertEqual(book.authors.count(), 1)
        author = book.authors.first()
        self.assertEqual(author.name, self.api_response["author_name"][0])

    # def test_existing_book(self):
    #     # create the Author and Book directly to simulate existing data
    #     author, author_created = AuthorFactory(
    #         key=self.api_response["author_key"][0],
    #         defaults={"name": self.api_response["author_name"][0]},
    #     )
    #     book, book_created = BookFactory(
    #         key=self.api_response["key"],
    #         defaults={
    #             "title": self.api_response["title"],
    #             "cover_url": f"http://covers.openlibrary.org/b/id/{self.api_response['cover_i']}-L.jpg",
    #             "publish_date": ", ".join(self.api_response["publish_date"]),
    #             "subjects": self.api_response["subject"],
    #             "isbns": self.api_response["isbn"],
    #         },
    #     )
    #     book.authors.add(author)
    #


"""
    example response of openlibrary (single book) {
        "_version_": 1795895391594479616,
        "already_read_count": 1,
        "author_facet": ["OL2643489A Jose Mauro De Vasconcelos"],
        "author_key": ["OL2643489A"],
        "author_name": ["Jose Mauro De Vasconcelos"], "cover_edition_key": "OL29832249M", "cover_i": 10413035,
        "currently_reading_count": 3,
        "ebook_access": "no_ebook",
        "ebook_count_i": 0,
        "edition_count": 3,
        "edition_key": ["OL29832249M", "OL33678463M", "OL28910961M"],
        "first_publish_year": 2011,
        "format": ["hardcover"],
        "has_fulltext": False,
        "isbn": [
            "964913980X",
            "9789649139807",
            "1782692452",
            "1536203289",
            "9781782692454",
            "9781536203288"
        ],
        "key": "/works/OL286593W",
        "language": ["eng"],
        "last_modified_i": 1705644839,
        "number_of_pages_median": 232,
        "public_scan_b": False,
        "publish_date": ["2019", "Mar 16, 2011"],
        "publish_year": [2011, 2019],
        "publisher": ["Pushkin Press, Limited", "Candlewick Press", "Rah-e Mana"],
        "publisher_facet": [
            "Candlewick Press",
            "Pushkin Press, Limited",
            "Rah-e Mana"
        ],
        "readinglog_count": 23,
        "seed": [
            "/books/OL29832249M",
            "/books/OL33678463M",
            "/books/OL28910961M",
            "/works/OL286593W",
            "/authors/OL2643489A",
            "/subjects/brazil_fiction",
            "/subjects/children's_fiction"
        ],
        "subject": ["Brazil, fiction", "Children's fiction"],
        "subject_facet": ["Brazil, fiction", "Children's fiction"],
        "subject_key": ["brazil_fiction", "children's_fiction"],
        "title": "My Sweet-orange Tree",
        "title_sort": "My Sweet-orange Tree",
        "title_suggest": "My Sweet-orange Tree",
        "type": "work",
        "want_to_read_count": 19
    }
    """

"""
{
    "name": "Jose Mauro De Vasconcelos",
    "last_modified": {
        "type": "/type/datetime",
        "value": "2008-04-29 13:35:46.87638"
    },
    "key": "/authors/OL2643489A",
    "type": {
        "key": "/type/author"
    },
    "id": 9968536,
    "revision": 1
}
"""
