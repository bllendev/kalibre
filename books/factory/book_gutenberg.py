import factory


class BookGutenbergFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "books.BookGutenberg"

    json = factory.LazyFunction(lambda: {"resources": [{"url": "http://example.com"}]})
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    subjects = factory.LazyFunction(lambda: ["fiction", "adventure"])
    bookshelves = factory.LazyFunction(lambda: ["public domain", "classics"])

    class Params:
        test_book = factory.Trait(
            title="Sample Book Title",
            subjects=["test subject"],
            bookshelves=["test shelf"],
        )
