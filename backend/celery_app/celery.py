"""
Celery application configuration.

Per ARCHITECTURE.md Section 8: Celery with Redis as the broker handles all
asynchronous and scheduled work (reminders, AI processing, notifications,
housekeeping). Queue separation and Celery Beat schedules are added as the
domains that need them are implemented (Milestones 5, 7, 8, 9).
"""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('mindmesh')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
