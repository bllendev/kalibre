import os
from django.conf import settings
import factory
import json


# test book constants
TEST_EMBEDDINGS_PATH = os.path.join(
    settings.BASE_DIR, "books", "tests", "_test_query_embeddings.json"
)

with open(TEST_EMBEDDINGS_PATH, "rb") as f:
    test_embeddings = json.load(f)


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "books.Book"

    class Params:
        test_book = factory.Trait(
            title="My Sweet-orange Tree",
            isbns=[
                "964913980X",
                "9789649139807",
                "1782692452",
                "1536203289",
                "9781782692454",
                "9781536203288",
            ],
            json_links=[],
        )

    id = factory.Faker("uuid4")
    title = factory.Faker("sentence", nb_words=3)
    isbns = []
    key = factory.Faker("bothify", text="/works/OL#####W")
    cover_url = factory.Faker("url")
    description = factory.Faker("paragraph")

    # Authors handled by post-generation
    publish_date = factory.LazyFunction(lambda: ["2019", "Mar 16, 2011"])
    subjects = factory.LazyFunction(
        lambda: ["Brazil, fiction", "Children's fiction"])
    price = factory.Faker("pydecimal", left_digits=3,
                          right_digits=2, positive=True)
    cover = None  # Typically a path to a local or test file

    # Assuming JSON links should be empty list by default like in your params
    json_links = factory.LazyFunction(list)
    vector_search = None  # Needs manual association if persisting

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        from ai.factory import VectorSearchFactory

        # If vector_search is None, create one with test embeddings
        if not kwargs.get("vector_search"):
            kwargs["vector_search"] = VectorSearchFactory.create(
                vector=test_embeddings,
                metadata={"source": "test"},
                # NOTE: we set saved embeddings to prevent
                # redundant api queries during testing...
            )

        return super()._create(model_class, *args, **kwargs)

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        from authors.factory.author import AuthorFactory

        if not create:
            # skip adding authors if not persisting to the database
            return
        if extracted:
            # add the specified authors
            for author in extracted:
                self.authors.add(author)
        else:
            # add a random author by default
            author = AuthorFactory()
