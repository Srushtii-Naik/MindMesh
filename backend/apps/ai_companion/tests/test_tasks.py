"""Tests for apps.ai_companion.tasks — the Celery task that runs memory
extraction off the chat request path (PROJECT_RULES.md Section 11).
CELERY_TASK_ALWAYS_EAGER=True in config/settings/test.py runs these
synchronously, so no broker is required."""

import uuid

import pytest

from apps.ai_companion.models import Conversation, MemoryFact, Message, MessageRole
from apps.ai_companion.tasks import extract_memory_from_message_task

pytestmark = pytest.mark.django_db


def test_task_extracts_and_stores_facts(user, conversation):
    message = Message.objects.create(
        conversation=conversation, role=MessageRole.USER, content='I live in Bengaluru.'
    )

    created_count = extract_memory_from_message_task(str(user.id), str(conversation.id), str(message.id))

    assert created_count >= 1
    assert MemoryFact.objects.filter(user=user).exists()


def test_task_returns_zero_for_missing_user():
    fake_conversation_id = uuid.uuid4()
    fake_message_id = uuid.uuid4()

    result = extract_memory_from_message_task(str(uuid.uuid4()), str(fake_conversation_id), str(fake_message_id))

    assert result == 0


def test_task_returns_zero_for_missing_conversation(user):
    result = extract_memory_from_message_task(str(user.id), str(uuid.uuid4()), str(uuid.uuid4()))
    assert result == 0


def test_task_returns_zero_for_missing_message(user, conversation):
    result = extract_memory_from_message_task(str(user.id), str(conversation.id), str(uuid.uuid4()))
    assert result == 0


def test_task_does_not_extract_from_other_users_conversation(user, other_user):
    foreign_conversation = Conversation.objects.create(user=other_user, title='Not mine')
    foreign_message = Message.objects.create(
        conversation=foreign_conversation, role=MessageRole.USER, content='I live in Mumbai.'
    )

    # Attempting to extract using `user`'s id against `other_user`'s
    # conversation must find nothing — ownership is enforced by the lookup.
    result = extract_memory_from_message_task(str(user.id), str(foreign_conversation.id), str(foreign_message.id))

    assert result == 0
