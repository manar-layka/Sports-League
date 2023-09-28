from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from factory import Faker, LazyAttribute, post_generation
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")
    name = Faker("name")

    password = LazyAttribute(lambda x: Faker(
        "password",
        length=42,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    ).evaluate(None, None, extra={"locale": None}))

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results and not cls._meta.skip_postgeneration_save:
            # Some post-generation hooks ran, and may have modified us.
            instance.save()

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]
