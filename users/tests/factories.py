import factory
import random
from django.contrib.auth import get_user_model


from translate.constants import LANGUAGES


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")
    email = factory.Faker("email")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if extracted:
            self.set_password(extracted)
            if create:
                self.save()


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.Email"

    address = factory.Faker("email")
    # translate_file = random.choice(list(LANGUAGES.keys()))
