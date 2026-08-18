"""
Celery tasks — Notifications (ARCHITECTURE.md Section 8: background jobs).

Task bodies are intentionally thin: they resolve the delivery/notification
row and delegate to services.py, which holds the actual send logic and is
independently unit-testable without exercising Celery's retry machinery.
`autoretry_for` + `retry_backoff` follows the same pattern already used in
apps/accounts/tasks.py and apps/ai_companion/tasks.py.
"""

from celery import shared_task


@shared_task(name='notifications.scan_due_reminders')
def scan_due_reminders_task() -> int:
    """
    Celery Beat periodic task (see settings.CELERY_BEAT_SCHEDULE) — the
    Milestone 9 "reminder engine" ROADMAP.md's checklist requires. Scans all
    users' due reminders and dispatches a notification (+ per-channel
    deliveries) for each, building on Milestone 5's Reminder data model.

    Returns the number of reminders processed (useful in logs/monitoring).
    """
    from apps.notifications.services import dispatch_due_reminder_notifications

    return dispatch_due_reminder_notifications()


@shared_task(
    name='notifications.deliver_email',
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def deliver_notification_email_task(delivery_id: str) -> None:
    """Delivers one notification by email. Retries (with backoff, up to 3
    times) on any failure; each attempt's outcome is recorded on the
    NotificationDelivery row by services.deliver_email_notification."""
    from apps.notifications.models import NotificationDelivery
    from apps.notifications.services import deliver_email_notification

    try:
        delivery = NotificationDelivery.objects.select_related('notification__user').get(
            id=delivery_id
        )
    except NotificationDelivery.DoesNotExist:
        return

    deliver_email_notification(delivery)


@shared_task(
    name='notifications.deliver_push',
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def deliver_notification_push_task(delivery_id: str) -> None:
    """Delivers one notification by push to every active device token the
    user has registered. Retries (with backoff, up to 3 times) if every
    device's send fails; outcome recorded by services.deliver_push_notification."""
    from apps.notifications.models import NotificationDelivery
    from apps.notifications.services import deliver_push_notification

    try:
        delivery = NotificationDelivery.objects.select_related('notification__user').get(
            id=delivery_id
        )
    except NotificationDelivery.DoesNotExist:
        return

    deliver_push_notification(delivery)
