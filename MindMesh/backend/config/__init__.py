"""
Ensures the Celery app (celery_app/celery.py) is loaded whenever Django
starts, so that `@shared_task`-decorated tasks anywhere in the project bind
to it — and therefore pick up its configuration (broker URL, eager-mode for
tests, etc.) — rather than an unconfigured default Celery app.
"""

from celery_app.celery import app as celery_app

__all__ = ('celery_app',)
