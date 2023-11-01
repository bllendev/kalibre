import factory
import uuid

from books.tests.constants import TEST_ISBN, TEST_BOOK_FILETYPE


# test book constants
TEST_TITLE = "My Sweet Little Orange Tree"
TEST_AUTHOR = "De Vasconcelos, José Mauro;Entrekin, Alison"
TEST_FILETYPE = TEST_BOOK_FILETYPE
ISBN = TEST_ISBN
JSON_LINKS ='[\"http://library.lol/main/CDD0C7BB84700F371E6F4675947D7456\", \"http://libgen.lc/ads.php?md5=CDD0C7BB84700F371E6F4675947D7456\", \"https://library.bz/main/edit/CDD0C7BB84700F371E6F4675947D7456\"]'


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "books.Book"

    class Params:
        test_book = factory.Trait(
            title=TEST_TITLE,
            author=TEST_AUTHOR,
            filetype=TEST_FILETYPE,
            isbn=TEST_ISBN,
            json_links=JSON_LINKS
        )

    id = uuid.uuid4()
    title = factory.Faker('sentence', nb_words=4)
    author = factory.Faker('name')
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    cover_url = factory.Faker('url')
    cover = factory.django.ImageField(filename='test_cover.jpg')
    filetype = factory.Faker('file_extension')
    isbn = factory.Faker('isbn13')
    json_links = {"link1": "http://example.com", "link2": "http://example2.com"}
