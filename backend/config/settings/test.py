from .base import *  # noqa: F403

SECRET_KEY = "olive-branch-test-only"
ALLOW_DEMO_SEED = True
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
