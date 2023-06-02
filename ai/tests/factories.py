import factory
from factory.django import DjangoModelFactory
from users.tests.factories import CustomUserFactory


class ConversationFactory(DjangoModelFactory):
    class Meta:
        model = "ai.Conversation"

    user = factory.SubFactory(CustomUserFactory)
    started_at = factory.Faker('date_time')
    last_updated = factory.Faker('date_time')


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = "ai.Message"

    conversation = factory.SubFactory(ConversationFactory)
    sender = factory.Iterator(['user', 'ai'])
    text = factory.Faker('paragraph')
    sent_at = factory.Faker('date_time')
