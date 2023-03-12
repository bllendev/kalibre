import factory
from django.contrib.auth import get_user_model


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.Email"

    address = factory.Faker('email')
    user = factory.SubFactory(get_user_model())


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()            # class CustomUser(AbstractUser):

    username = factory.Faker('user_name')
    email = factory.Faker('email')

    @factory.post_generation
    def email_addresses(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for email in extracted:
                self.email_addresses.add(email)
