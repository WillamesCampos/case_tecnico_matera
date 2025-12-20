import factory
from django.contrib.auth import get_user_model

from credit_track.test_settings import FAKER_GENERATOR

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.LazyAttribute(
        lambda username: FAKER_GENERATOR.user_name()
    )
    email = factory.LazyAttribute(lambda email: FAKER_GENERATOR.email())
    password = factory.PostGenerationMethodCall("set_password")

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or "1234"
        self.set_password(password)
        self.save()

    class Meta:
        model = User
        django_get_or_create = ("username",)
