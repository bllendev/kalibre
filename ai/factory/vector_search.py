import factory
import random


class VectorSearchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "ai.VectorSearch"

    vector = factory.LazyFunction(
        lambda: [random.uniform(-1, 1) for _ in range(VectorSearch.DIMENSION)]
    )
    metadata = factory.LazyFunction(
        lambda: {"source": "generated", "description": "Generated for testing"}
    )
    created_at = factory.Faker(
        "date_time_this_century", before_now=True, after_now=False, tzinfo=None
    )
    updated_at = factory.Faker(
        "date_time_this_century", before_now=True, after_now=False, tzinfo=None
    )
