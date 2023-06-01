import factory


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.CustomUser"           # class CustomUser(AbstractUser):

    id = factory.Faker('pyint')
    email_addresses = factory.RelatedFactory("users.tests.factories.EmailFactory")


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.Email"

    address = factory.Faker('email')
