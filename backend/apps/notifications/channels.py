"""
Push notification delivery abstraction.

ARCHITECTURE.md Section 4 lists "channel (push/email/in-app)" as part of
the Notifications entity group. No push vendor (FCM/APNs/Web Push)
credentials exist yet, so — mirroring the precedent already established by
AI_PROVIDER's `stub` adapter (apps/ai_companion/providers.py) and
EMAIL_BACKEND's `console` adapter (config/settings/base.py) — the default
adapter here simply logs what it would have sent instead of calling a real
vendor API. This keeps the notification pipeline fully runnable and
testable without third-party push credentials, while the abstraction itself
(`PushSender`) means swapping in a real vendor later is a new adapter class
plus one settings change (PUSH_PROVIDER) — never a change to service-layer
or task code, per PROJECT_RULES.md Section 3 (open/closed) and Section 10's
"provider independent" principle applied to this channel too.
"""

from __future__ import annotations

import abc
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class PushDeliveryError(Exception):
    """Raised when a push adapter fails to deliver to a device token, or
    when PUSH_PROVIDER names an adapter that doesn't exist."""


class PushSender(abc.ABC):
    """Provider-agnostic contract. Concrete adapters translate this into a
    vendor-specific push API call; domain code only ever depends on this
    interface, never on a specific adapter (mirrors AIProvider's shape)."""

    @abc.abstractmethod
    def send(self, *, token: str, title: str, body: str) -> None:
        """Deliver a push notification to `token`. Raises PushDeliveryError
        (or lets a vendor SDK's own exception propagate) on failure."""
        raise NotImplementedError


class ConsolePushSender(PushSender):
    """
    Default adapter — logs the push instead of calling a real vendor.

    Deliberately never fails on its own (logging can't meaningfully fail in
    a way callers should retry for), so this adapter always reports success
    — a faithful stand-in for "delivery succeeded" until a real vendor
    adapter is wired in.
    """

    def send(self, *, token: str, title: str, body: str) -> None:
        logger.info('PUSH [console] -> token=%s… title=%r body=%r', token[:12], title, body)


def get_push_sender() -> PushSender:
    """Selects the push adapter per settings.PUSH_PROVIDER, mirroring
    apps.ai_companion.providers.get_provider's env-driven adapter
    selection."""
    provider = settings.PUSH_PROVIDER
    if provider == 'console':
        return ConsolePushSender()
    raise PushDeliveryError(f'Unsupported PUSH_PROVIDER: {provider!r}')
