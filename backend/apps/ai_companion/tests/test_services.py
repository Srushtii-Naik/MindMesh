"""Unit tests for apps.ai_companion.services — the cross-domain entry point
other apps (e.g. apps.notes) call into, plus Milestone 7's conversational
surface (context assembly, conversations, chat, memory extraction,
AI-enhanced suggestions). Uses the default StubProvider (config/settings/
test.py sets AI_PROVIDER='stub') so these run fully offline.
"""

import pytest
from django.utils import timezone

from apps.ai_companion.models import Conversation, MemoryCategory, MemoryFact, Message, MessageRole
from apps.ai_companion.services import (
    ChatResponseError,
    ConversationNotFoundError,
    DuplicateMemoryFactError,
    EmptyMessageError,
    MemoryFactNotFoundError,
    SummarizationError,
    assemble_context_for_user,
    create_conversation_for_user,
    delete_conversation_for_user,
    delete_memory_fact_for_user,
    extract_and_store_memory_from_message,
    get_ai_enhanced_suggestions,
    get_conversation,
    get_memory_fact,
    list_conversations,
    list_memory_facts,
    list_messages,
    send_message_for_user,
    summarize_text,
    update_memory_fact_for_user,
)

pytestmark = pytest.mark.django_db


def test_summarize_text_returns_a_summary():
    text = 'The quick brown fox jumps. It jumps over the lazy dog. The dog does not mind.'

    summary = summarize_text(text, max_sentences=2)

    assert summary == 'The quick brown fox jumps. It jumps over the lazy dog.'


def test_summarize_text_rejects_empty_content():
    with pytest.raises(SummarizationError):
        summarize_text('   ')


def test_summarize_text_strips_whitespace_before_summarizing():
    summary = summarize_text('   A single note.   ', max_sentences=1)
    assert summary == 'A single note.'


# --------------------------------------------------------------------------
# Context Assembly Service
# --------------------------------------------------------------------------


class TestAssembleContextForUser:
    def test_returns_empty_string_when_user_has_no_data(self, user):
        assert assemble_context_for_user(user) == ''

    def test_includes_overdue_and_due_today_task_counts(self, user):
        from apps.tasks.models import Task

        today = timezone.localdate()
        Task.objects.create(user=user, title='Overdue thing', due_date=today.replace(day=1))
        Task.objects.create(user=user, title='Due today thing', due_date=today)

        context = assemble_context_for_user(user)

        assert 'overdue' in context.lower()
        assert 'due today' in context.lower()

    def test_includes_recent_note_titles(self, user):
        from apps.notes.models import Note

        Note.objects.create(user=user, title='Doctor appointment', content='Notes here.')

        context = assemble_context_for_user(user)

        assert 'Doctor appointment' in context

    def test_includes_known_memory_facts(self, user):
        from apps.ai_companion.models import MemoryFact

        MemoryFact.objects.create(user=user, fact_text='Prefers tea over coffee')

        context = assemble_context_for_user(user)

        assert 'Prefers tea over coffee' in context

    def test_groups_memory_facts_by_category(self, user):
        from apps.ai_companion.models import MemoryFact

        MemoryFact.objects.create(
            user=user, fact_text='Prefers tea over coffee', category=MemoryCategory.PREFERENCE
        )
        MemoryFact.objects.create(
            user=user, fact_text="Daughter's birthday is June 3rd", category=MemoryCategory.IMPORTANT_DATE
        )

        context = assemble_context_for_user(user)

        assert 'Preferences: Prefers tea over coffee.' in context
        assert "Important dates: Daughter's birthday is June 3rd." in context

    def test_excludes_deleted_memory_facts(self, user):
        from apps.ai_companion.models import MemoryFact

        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea over coffee')
        delete_memory_fact_for_user(user, fact.id)

        context = assemble_context_for_user(user)

        assert 'Prefers tea over coffee' not in context


# --------------------------------------------------------------------------
# Conversations
# --------------------------------------------------------------------------


class TestConversations:
    def test_create_conversation_for_user(self, user):
        conversation = create_conversation_for_user(user, title='Planning my week')
        assert conversation.user == user
        assert conversation.title == 'Planning my week'

    def test_list_conversations_only_returns_own_active_conversations(self, user, other_user):
        Conversation.objects.create(user=user, title='Mine')
        Conversation.objects.create(user=other_user, title='Not mine')

        conversations = list(list_conversations(user))

        assert len(conversations) == 1
        assert conversations[0].title == 'Mine'

    def test_get_conversation_raises_for_missing_conversation(self, user):
        import uuid

        with pytest.raises(ConversationNotFoundError):
            get_conversation(user, uuid.uuid4())

    def test_get_conversation_raises_for_other_users_conversation(self, user, other_user):
        foreign = Conversation.objects.create(user=other_user, title='Not mine')
        with pytest.raises(ConversationNotFoundError):
            get_conversation(user, foreign.id)

    def test_delete_conversation_soft_deletes(self, user, conversation):
        delete_conversation_for_user(user, conversation.id)
        conversation.refresh_from_db()
        assert conversation.is_active is False
        assert conversation.deleted_at is not None

    def test_deleted_conversation_no_longer_listed(self, user, conversation):
        delete_conversation_for_user(user, conversation.id)
        assert list(list_conversations(user)) == []


# --------------------------------------------------------------------------
# Messages / Chat
# --------------------------------------------------------------------------


class TestSendMessage:
    def test_send_message_persists_user_and_assistant_messages(self, user, conversation):
        assistant_message = send_message_for_user(user, conversation.id, content='Hello!')

        messages = list(list_messages(user, conversation.id))
        assert len(messages) == 2
        assert messages[0].role == MessageRole.USER
        assert messages[0].content == 'Hello!'
        assert messages[1].role == MessageRole.ASSISTANT
        assert messages[1].id == assistant_message.id

    def test_send_message_rejects_empty_content(self, user, conversation):
        with pytest.raises(EmptyMessageError):
            send_message_for_user(user, conversation.id, content='   ')

    def test_send_message_raises_for_conversation_not_owned(self, user, other_user):
        foreign = Conversation.objects.create(user=other_user, title='Not mine')
        with pytest.raises(ConversationNotFoundError):
            send_message_for_user(user, foreign.id, content='Hi')

    def test_send_message_derives_title_from_first_message(self, user, conversation):
        conversation.title = ''
        conversation.save()

        send_message_for_user(user, conversation.id, content='What should I focus on today?')

        conversation.refresh_from_db()
        assert conversation.title == 'What should I focus on today?'

    def test_send_message_does_not_overwrite_existing_title(self, user, conversation):
        assert conversation.title == 'Getting organized'

        send_message_for_user(user, conversation.id, content='Second message')

        conversation.refresh_from_db()
        assert conversation.title == 'Getting organized'

    def test_send_message_touches_conversation_updated_at(self, user, conversation):
        original_updated_at = conversation.updated_at

        send_message_for_user(user, conversation.id, content='Hello!')

        conversation.refresh_from_db()
        assert conversation.updated_at >= original_updated_at

    def test_send_message_reply_reflects_assembled_context(self, user, conversation):
        from apps.tasks.models import Task

        today = timezone.localdate()
        Task.objects.create(user=user, title='Overdue thing', due_date=today.replace(day=1))

        assistant_message = send_message_for_user(user, conversation.id, content='Any advice?')

        assert 'overdue' in assistant_message.content.lower()

    def test_send_message_enqueues_memory_extraction(self, user, conversation):
        """CELERY_TASK_ALWAYS_EAGER=True in test settings runs the task
        synchronously, so a durable statement produces a stored MemoryFact
        by the time send_message_for_user returns."""
        from apps.ai_companion.models import MemoryFact

        send_message_for_user(user, conversation.id, content='I live in Bengaluru.')

        facts = list(MemoryFact.objects.filter(user=user))
        assert any('bengaluru' in fact.fact_text.lower() for fact in facts)


class TestChatResponseErrorHandling:
    def test_provider_failure_raises_chat_response_error(self, user, conversation, monkeypatch):
        from apps.ai_companion import services as ai_services
        from apps.ai_companion.providers import AIProviderError

        class _FailingProvider:
            def generate_response(self, *args, **kwargs):
                raise AIProviderError('provider unavailable')

        monkeypatch.setattr(ai_services, 'get_ai_provider', lambda: _FailingProvider())

        with pytest.raises(ChatResponseError):
            send_message_for_user(user, conversation.id, content='Hello?')


# --------------------------------------------------------------------------
# Memory extraction
# --------------------------------------------------------------------------


class TestMemoryExtraction:
    def test_extracts_and_stores_new_facts(self, user, conversation):
        message = Message.objects.create(
            conversation=conversation, role=MessageRole.USER, content='I am a teacher.'
        )

        created = extract_and_store_memory_from_message(user, conversation, message)

        assert len(created) >= 1
        assert list(list_memory_facts(user))

    def test_does_not_duplicate_existing_facts(self, user, conversation):
        from apps.ai_companion.models import MemoryFact

        MemoryFact.objects.create(user=user, fact_text='I am a teacher')
        message = Message.objects.create(
            conversation=conversation, role=MessageRole.USER, content='I am a teacher.'
        )

        extract_and_store_memory_from_message(user, conversation, message)

        assert MemoryFact.objects.filter(user=user, fact_text__iexact='I am a teacher').count() == 1

    def test_skips_assistant_messages(self, user, conversation):
        message = Message.objects.create(
            conversation=conversation, role=MessageRole.ASSISTANT, content='I am here to help.'
        )

        created = extract_and_store_memory_from_message(user, conversation, message)

        assert created == []

    def test_no_facts_for_non_factual_message(self, user, conversation):
        message = Message.objects.create(
            conversation=conversation, role=MessageRole.USER, content='What time is it?'
        )

        created = extract_and_store_memory_from_message(user, conversation, message)

        assert created == []

    def test_extracted_facts_are_categorized(self, user, conversation):
        """ROADMAP.md Milestone 8: extraction classifies each new fact via
        apps.ai_companion.providers.categorize_memory_fact."""
        message = Message.objects.create(
            conversation=conversation, role=MessageRole.USER, content='I prefer tea over coffee.'
        )

        created = extract_and_store_memory_from_message(user, conversation, message)

        assert created
        assert all(fact.category == MemoryCategory.PREFERENCE for fact in created)

    def test_uncategorized_fact_defaults_to_personal_fact(self, user, conversation):
        message = Message.objects.create(
            conversation=conversation, role=MessageRole.USER, content='I am a nurse.'
        )

        created = extract_and_store_memory_from_message(user, conversation, message)

        assert created
        assert all(fact.category == MemoryCategory.PERSONAL_FACT for fact in created)

    def test_does_not_duplicate_against_soft_deleted_and_active_facts_correctly(self, user, conversation):
        """A soft-deleted fact should not block re-extraction of the same
        fact text (the unique constraint is scoped to active facts only)."""
        existing = MemoryFact.objects.create(user=user, fact_text='I am a teacher')
        delete_memory_fact_for_user(user, existing.id)

        message = Message.objects.create(
            conversation=conversation, role=MessageRole.USER, content='I am a teacher.'
        )
        created = extract_and_store_memory_from_message(user, conversation, message)

        assert len(created) >= 1


# --------------------------------------------------------------------------
# AI-enhanced suggestions
# --------------------------------------------------------------------------


class TestAIEnhancedSuggestions:
    def test_returns_empty_list_when_no_rule_based_suggestions(self, user):
        assert get_ai_enhanced_suggestions(user) == []

    def test_appends_ai_proactive_suggestion_when_context_available(self, user):
        from apps.tasks.models import Task

        today = timezone.localdate()
        Task.objects.create(user=user, title='Overdue thing', due_date=today.replace(day=1))

        suggestions = get_ai_enhanced_suggestions(user)

        kinds = [s['kind'] for s in suggestions]
        assert 'overdue' in kinds
        assert 'ai_proactive' in kinds

    def test_degrades_to_rule_based_suggestions_on_provider_failure(self, user, monkeypatch):
        from apps.tasks.models import Task

        today = timezone.localdate()
        Task.objects.create(user=user, title='Overdue thing', due_date=today.replace(day=1))

        from apps.ai_companion import services as ai_services
        from apps.ai_companion.providers import AIProviderError

        class _FailingProvider:
            def generate_response(self, *args, **kwargs):
                raise AIProviderError('provider unavailable')

        monkeypatch.setattr(ai_services, 'get_ai_provider', lambda: _FailingProvider())

        suggestions = get_ai_enhanced_suggestions(user)

        assert all(s['kind'] != 'ai_proactive' for s in suggestions)
        assert any(s['kind'] == 'overdue' for s in suggestions)


# --------------------------------------------------------------------------
# Memory Engine (ROADMAP.md Milestone 8) — view/edit/delete controls,
# category filtering, and recall demonstrably persisting across sessions.
# --------------------------------------------------------------------------


class TestMemoryFactCrud:
    def test_list_memory_facts_only_returns_own_active_facts(self, user, other_user):
        MemoryFact.objects.create(user=user, fact_text='Mine')
        MemoryFact.objects.create(user=other_user, fact_text='Not mine')
        deleted = MemoryFact.objects.create(user=user, fact_text='Deleted')
        delete_memory_fact_for_user(user, deleted.id)

        facts = list(list_memory_facts(user))

        assert [f.fact_text for f in facts] == ['Mine']

    def test_list_memory_facts_filters_by_category(self, user):
        MemoryFact.objects.create(user=user, fact_text='Likes tea', category=MemoryCategory.PREFERENCE)
        MemoryFact.objects.create(user=user, fact_text='Is a teacher', category=MemoryCategory.PERSONAL_FACT)

        facts = list(list_memory_facts(user, category=MemoryCategory.PREFERENCE))

        assert [f.fact_text for f in facts] == ['Likes tea']

    def test_get_memory_fact_raises_for_missing_fact(self, user):
        import uuid

        with pytest.raises(MemoryFactNotFoundError):
            get_memory_fact(user, uuid.uuid4())

    def test_get_memory_fact_raises_for_other_users_fact(self, user, other_user):
        foreign = MemoryFact.objects.create(user=other_user, fact_text='Not mine')
        with pytest.raises(MemoryFactNotFoundError):
            get_memory_fact(user, foreign.id)

    def test_update_memory_fact_edits_text_and_category(self, user):
        fact = MemoryFact.objects.create(
            user=user, fact_text='Old text', category=MemoryCategory.PERSONAL_FACT
        )

        updated = update_memory_fact_for_user(
            user, fact.id, fact_text='New text', category=MemoryCategory.PREFERENCE
        )

        assert updated.fact_text == 'New text'
        assert updated.category == MemoryCategory.PREFERENCE

    def test_update_memory_fact_rejects_duplicate_text(self, user):
        MemoryFact.objects.create(user=user, fact_text='Prefers tea')
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers coffee')

        with pytest.raises(DuplicateMemoryFactError):
            update_memory_fact_for_user(user, fact.id, fact_text='Prefers tea')

    def test_update_memory_fact_raises_for_missing_fact(self, user):
        import uuid

        with pytest.raises(MemoryFactNotFoundError):
            update_memory_fact_for_user(user, uuid.uuid4(), fact_text='New text')

    def test_delete_memory_fact_soft_deletes(self, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')

        delete_memory_fact_for_user(user, fact.id)

        fact.refresh_from_db()
        assert fact.is_active is False
        assert fact.deleted_at is not None

    def test_deleted_memory_fact_no_longer_listed(self, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')
        delete_memory_fact_for_user(user, fact.id)

        assert list(list_memory_facts(user)) == []

    def test_delete_memory_fact_raises_for_other_users_fact(self, user, other_user):
        foreign = MemoryFact.objects.create(user=other_user, fact_text='Not mine')
        with pytest.raises(MemoryFactNotFoundError):
            delete_memory_fact_for_user(user, foreign.id)


class TestMemoryRecallAcrossSessions:
    def test_stored_fact_influences_reply_in_a_later_new_conversation(self, user):
        """ROADMAP.md Milestone 8: 'AI recall demonstrably influences
        responses in later sessions' — a fact learned in one conversation
        must shape the assistant's reply in a brand-new conversation."""
        first_conversation = create_conversation_for_user(user, title='First session')
        send_message_for_user(user, first_conversation.id, content='I prefer tea over coffee.')

        assert list(list_memory_facts(user))

        second_conversation = create_conversation_for_user(user, title='Later session')
        reply = send_message_for_user(user, second_conversation.id, content='Any advice for me?')

        assert 'tea' in reply.content.lower()
