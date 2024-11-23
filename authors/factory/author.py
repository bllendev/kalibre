import factory


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "authors.Author"

    id = factory.Faker("uuid4")
    key = factory.Faker("bothify", text="/authors/OL#####A")
    name = factory.Faker("name")
    birth_date = factory.Faker("date")
