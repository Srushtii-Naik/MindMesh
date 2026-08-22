"""
Repository / data-access layer — AI Companion.

Encapsulates ORM queries for Conversation, Message, and MemoryFact,
isolating persistence details from the service layer, per ARCHITECTURE.md
Section 3. Every query here is scoped to a given user — row-level
ownership per PROJECT_RULES.md Section 7.
"""

from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.ai_companion.models import Conversation, MemoryFact, Message

# --------------------------------------------------------------------------
# Conversation
# --------------------------------------------------------------------------


def list_conversations_for_user(user: User) -> QuerySet[Conversation]:
    return Conversation.objects.filter(user=user, is_active=True)


def get_conversation_for_user(user: User, conversation_id) -> Conversation | None:
    return Conversation.objects.filter(user=user, id=conversation_id, is_active=True).first()


def create_conversation(*, user: User, title: str = '') -> Conversation:
    return Conversation.objects.create(user=user, title=title)


def update_conversation(conversation: Conversation, **fields) -> Conversation:
    for field, value in fields.items():
        setattr(conversation, field, value)
    conversation.save()
    return conversation


def soft_delete_conversation(conversation: Conversation) -> None:
    conversation.is_active = False
    conversation.deleted_at = timezone.now()
    conversation.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


def touch_conversation(conversation: Conversation) -> None:
    """Bumps `updated_at` so the conversation list sorts most-recently-active first."""
    conversation.save(update_fields=['updated_at'])


# --------------------------------------------------------------------------
# Message
# --------------------------------------------------------------------------


def list_messages_for_conversation(conversation: Conversation) -> QuerySet[Message]:
    return Message.objects.filter(conversation=conversation)


def create_message(*, conversation: Conversation, role: str, content: str) -> Message:
    return Message.objects.create(conversation=conversation, role=role, content=content)


def get_message_for_conversation(conversation: Conversation, message_id) -> Message | None:
    return Message.objects.filter(conversation=conversation, id=message_id).first()


# --------------------------------------------------------------------------
# MemoryFact
# --------------------------------------------------------------------------


def list_memory_facts_for_user(user: User, *, category: str | None = None) -> QuerySet[MemoryFact]:
    queryset = MemoryFact.objects.filter(user=user, is_active=True)
    if category:
        queryset = queryset.filter(category=category)
    return queryset


def get_memory_fact_for_user(user: User, fact_id) -> MemoryFact | None:
    return MemoryFact.objects.filter(user=user, id=fact_id, is_active=True).first()


def memory_fact_exists_for_user(user: User, fact_text: str, *, exclude_id=None) -> bool:
    queryset = MemoryFact.objects.filter(user=user, is_active=True, fact_text__iexact=fact_text)
    if exclude_id is not None:
        queryset = queryset.exclude(id=exclude_id)
    return queryset.exists()


def create_memory_fact(
    *,
    user: User,
    fact_text: str,
    category: str,
    source_conversation: Conversation | None = None,
) -> MemoryFact:
    return MemoryFact.objects.create(
        user=user, fact_text=fact_text, category=category, source_conversation=source_conversation
    )


def update_memory_fact(fact: MemoryFact, **fields) -> MemoryFact:
    for field, value in fields.items():
        setattr(fact, field, value)
    fact.save()
    return fact


def soft_delete_memory_fact(fact: MemoryFact) -> None:
    fact.is_active = False
    fact.deleted_at = timezone.now()
    fact.save(update_fields=['is_active', 'deleted_at', 'updated_at'])
