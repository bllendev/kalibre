
import factory

class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "authors.Author"

    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    alias = factory.Faker('word')
    birth_date = factory.Faker('date_of_birth')
    death_date = factory.Faker('date_this_century')
    webpage = factory.Faker('url')
