"""
Celery tasks — AI Companion (ARCHITECTURE.md Section 8; registered with
celery_app via app.autodiscover_tasks()).

Memory extraction runs a second AI-provider call per user message, which is
exactly the kind of slow/bursty, provider-dependent work PROJECT_RULES.md
Section 11 calls out for Celery ("Any slow or bursty workload — AI calls...
runs asynchronously through Celery, never blocking the request-response
cycle"). Keeping it off the chat request path is what lets
apps.ai_companion.services.send_message_for_user return the assistant's
reply as soon as it's generated, rather than waiting on a second provider
round-trip the user isn't looking at.
"""

from celery import shared_task


@shared_task(
    name='ai_companion.extract_memory_from_message',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def extract_memory_from_message_task(user_id: str, conversation_id: str, message_id: str) -> int:
    """Runs memory extraction for one user message and persists any new
    facts. Returns the number of new facts stored (0 is the common case —
    most messages carry nothing durable)."""
    from apps.accounts.models import User
    from apps.ai_companion.models import Conversation, Message
    from apps.ai_companion.services import extract_and_store_memory_from_message

    try:
        user = User.objects.get(id=user_id)
        conversation = Conversation.objects.get(id=conversation_id, user=user)
        message = Message.objects.get(id=message_id, conversation=conversation)
    except (User.DoesNotExist, Conversation.DoesNotExist, Message.DoesNotExist):
        # The user/conversation/message may have been deleted between the
        # chat request and this task running — nothing to extract from.
        return 0

    created_facts = extract_and_store_memory_from_message(user, conversation, message)
    return len(created_facts)
