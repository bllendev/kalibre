import factory


class ConversationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "ai.Conversation"

    user = factory.SubFactory("users.tests.factories.CustomUserFactory")
    started_at = factory.Faker('date_time')
    last_updated = factory.Faker('date_time')


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "ai.Message"

    conversation = factory.SubFactory(ConversationFactory)
    sender = factory.Iterator(['user', 'ai'])
    text = factory.Faker('paragraph')
    sent_at = factory.Faker('date_time')
