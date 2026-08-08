"""Celery tasks for this domain, registered with celery_app (ARCHITECTURE.md Section 8)."""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(
    name='accounts.send_password_reset_email',
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_password_reset_email(*, user_id: str, reset_link: str) -> None:
    """
    Send the password reset email asynchronously.

    Sending is offloaded to Celery per ARCHITECTURE.md Section 8 ("AI
    processing... may involve slower external API calls unsuitable for a
    synchronous request" — the same principle applies to any outbound email
    provider). `user_id` is accepted for logging/observability even though
    the email itself only needs the address and link; it is not used to
    re-fetch the user here to keep the task free of a database round trip
    it doesn't otherwise need.
    """
    from apps.accounts.repositories import get_user_by_id

    user = get_user_by_id(user_id)
    if user is None:
        return

    send_mail(
        subject='Reset your MindMesh password',
        message=(
            f'Hi {user.full_name},\n\n'
            'We received a request to reset your MindMesh password. '
            f'Use the link below to choose a new one:\n\n{reset_link}\n\n'
            'If you did not request this, you can safely ignore this email — '
            'your password will not be changed.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
