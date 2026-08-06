"""Development settings — used by local Docker Compose / manage.py runserver."""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ['*']
