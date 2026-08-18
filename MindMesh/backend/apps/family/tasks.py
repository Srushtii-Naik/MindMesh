"""
Celery tasks — Family & Shared Workspace (ARCHITECTURE.md Section 8:
background jobs).

Task bodies are intentionally thin: they delegate to services.py, mirroring
apps/notifications/tasks.py.
"""

from celery import shared_task


@shared_task(name='family.expire_stale_invitations')
def expire_stale_invitations_task() -> int:
    """Celery Beat periodic task (see settings.CELERY_BEAT_SCHEDULE) —
    housekeeping that marks pending invitations past their expiry as
    EXPIRED. Returns the number of invitations expired."""
    from apps.family.services import expire_stale_invitations

    return expire_stale_invitations()
