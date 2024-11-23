import factory


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "ai.Message"

    conversation = factory.SubFactory("ai.factory.ConversationFactory")
    sender = factory.Iterator(["user", "ai"])
    text = factory.Faker("paragraph")
    sent_at = factory.Faker("date_time")
