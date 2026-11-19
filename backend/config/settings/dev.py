import os

from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = "olive-branch-local-development-only"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(
    ","
)
ALLOW_DEMO_SEED = True

USE_X_FORWARDED_HOST = True
