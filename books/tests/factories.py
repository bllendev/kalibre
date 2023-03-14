import factory
import uuid


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "books.Book"

    id = uuid.uuid4()
    title = factory.Faker('sentence', nb_words=4)
    author = factory.Faker('name')
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    cover = factory.django.ImageField(filename='test_cover.jpg')
    filetype = factory.Faker('file_extension')
    isbn = factory.Faker('isbn13')
    json_links = {"link1": "http://example.com", "link2": "http://example2.com"}