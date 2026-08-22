"""Shared fixtures for ai_companion app tests."""

import pytest

from apps.ai_companion.models import Conversation, Message, MessageRole


@pytest.fixture
def conversation(user) -> Conversation:
    return Conversation.objects.create(user=user, title='Getting organized')


@pytest.fixture
def user_message(conversation) -> Message:
    return Message.objects.create(
        conversation=conversation, role=MessageRole.USER, content='Hello there.'
    )
