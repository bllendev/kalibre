import factory
import random
from django.contrib.auth import get_user_model


from translate.constants import LANGUAGES


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = "default_user"
    email = factory.Faker('email')

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password("default_password")

class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.Email"

    address = factory.Faker('email')
    translate_file = random.choice(list(LANGUAGES.keys()))
