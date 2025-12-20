from .settings import *

import faker

FAKER_GENERATOR = faker.Faker(locale='pt_BR')

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
