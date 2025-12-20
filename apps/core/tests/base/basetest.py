import pytest

from credit_track.test_settings import FAKER_GENERATOR


class BaseTestCase:
    pytestmark = pytest.mark.django_db
    faker_generator = FAKER_GENERATOR

    def authenticate_user(self, client, user):
        client.force_authenticate(user=user)
