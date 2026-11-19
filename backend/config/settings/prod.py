import os

from .base import *  # noqa: F403

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")
DATABASES["default"]["PASSWORD"] = os.environ["POSTGRES_PASSWORD"]  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
