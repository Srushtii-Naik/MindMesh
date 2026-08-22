"""API tests for apps.ai_companion.views — success paths, validation
failures, and ownership/permission boundaries, per PROJECT_RULES.md
Section 12 ("API tests... success paths, validation failures, and
permission boundaries")."""

import uuid

import pytest
from django.urls import reverse

from apps.ai_companion.models import Conversation, MemoryFact, Message, MessageRole

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------
# Conversations
# --------------------------------------------------------------------------


class TestConversationListCreateView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(reverse('ai-conversation-list'))
        assert response.status_code == 401

    def test_create_conversation(self, auth_client):
        response = auth_client.post(reverse('ai-conversation-list'), {'title': 'My plans'})
        assert response.status_code == 201
        assert response.json()['title'] == 'My plans'

    def test_create_conversation_without_title(self, auth_client):
        response = auth_client.post(reverse('ai-conversation-list'), {})
        assert response.status_code == 201
        assert response.json()['title'] == ''

    def test_list_only_returns_own_conversations(self, auth_client, user, other_user):
        Conversation.objects.create(user=user, title='Mine')
        Conversation.objects.create(user=other_user, title='Not mine')

        response = auth_client.get(reverse('ai-conversation-list'))

        assert response.status_code == 200
        titles = [c['title'] for c in response.json()]
        assert titles == ['Mine']


class TestConversationDetailView:
    def test_retrieve_own_conversation(self, auth_client, conversation):
        response = auth_client.get(reverse('ai-conversation-detail', kwargs={'conversation_id': conversation.id}))
        assert response.status_code == 200
        assert response.json()['id'] == str(conversation.id)

    def test_retrieve_missing_conversation_returns_404(self, auth_client):
        response = auth_client.get(reverse('ai-conversation-detail', kwargs={'conversation_id': uuid.uuid4()}))
        assert response.status_code == 404

    def test_retrieve_other_users_conversation_returns_404(self, auth_client, other_user):
        foreign = Conversation.objects.create(user=other_user, title='Not mine')
        response = auth_client.get(reverse('ai-conversation-detail', kwargs={'conversation_id': foreign.id}))
        assert response.status_code == 404

    def test_delete_conversation_soft_deletes(self, auth_client, conversation):
        response = auth_client.delete(
            reverse('ai-conversation-detail', kwargs={'conversation_id': conversation.id})
        )
        assert response.status_code == 204

        conversation.refresh_from_db()
        assert conversation.is_active is False

    def test_delete_other_users_conversation_returns_404(self, auth_client, other_user):
        foreign = Conversation.objects.create(user=other_user, title='Not mine')
        response = auth_client.delete(
            reverse('ai-conversation-detail', kwargs={'conversation_id': foreign.id})
        )
        assert response.status_code == 404


# --------------------------------------------------------------------------
# Messages / Chat
# --------------------------------------------------------------------------


class TestMessageListCreateView:
    def test_requires_authentication(self, api_client, conversation):
        response = api_client.post(
            reverse('ai-message-list', kwargs={'conversation_id': conversation.id}), {'content': 'Hi'}
        )
        assert response.status_code == 401

    def test_send_message_returns_assistant_reply(self, auth_client, conversation):
        response = auth_client.post(
            reverse('ai-message-list', kwargs={'conversation_id': conversation.id}),
            {'content': 'Hello there!'},
        )

        assert response.status_code == 201
        body = response.json()
        assert body['role'] == 'assistant'
        assert body['content'] != ''

    def test_send_message_rejects_blank_content(self, auth_client, conversation):
        response = auth_client.post(
            reverse('ai-message-list', kwargs={'conversation_id': conversation.id}),
            {'content': '   '},
        )
        assert response.status_code == 400

    def test_send_message_rejects_missing_content(self, auth_client, conversation):
        response = auth_client.post(
            reverse('ai-message-list', kwargs={'conversation_id': conversation.id}), {}
        )
        assert response.status_code == 400

    def test_send_message_to_other_users_conversation_returns_404(self, auth_client, other_user):
        foreign = Conversation.objects.create(user=other_user, title='Not mine')
        response = auth_client.post(
            reverse('ai-message-list', kwargs={'conversation_id': foreign.id}), {'content': 'Hi'}
        )
        assert response.status_code == 404

    def test_list_conversation_history(self, auth_client, conversation, user_message):
        Message.objects.create(conversation=conversation, role=MessageRole.ASSISTANT, content='Hi there!')

        response = auth_client.get(reverse('ai-message-list', kwargs={'conversation_id': conversation.id}))

        assert response.status_code == 200
        results = response.json()['results']
        assert len(results) == 2
        assert results[0]['content'] == user_message.content

    def test_list_history_for_other_users_conversation_returns_404(self, auth_client, other_user):
        foreign = Conversation.objects.create(user=other_user, title='Not mine')
        response = auth_client.get(reverse('ai-message-list', kwargs={'conversation_id': foreign.id}))
        assert response.status_code == 404


# --------------------------------------------------------------------------
# Suggestions & Memory
# --------------------------------------------------------------------------


class TestAISuggestionsView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(reverse('ai-suggestions'))
        assert response.status_code == 401

    def test_returns_empty_list_when_nothing_to_suggest(self, auth_client):
        response = auth_client.get(reverse('ai-suggestions'))
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_suggestions_including_ai_proactive_entry(self, auth_client, user):
        from django.utils import timezone

        from apps.tasks.models import Task

        today = timezone.localdate()
        Task.objects.create(user=user, title='Overdue thing', due_date=today.replace(day=1))

        response = auth_client.get(reverse('ai-suggestions'))

        assert response.status_code == 200
        kinds = [s['kind'] for s in response.json()]
        assert 'overdue' in kinds
        assert 'ai_proactive' in kinds


class TestMemoryFactListView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(reverse('ai-memory-list'))
        assert response.status_code == 401

    def test_lists_only_own_memory_facts(self, auth_client, user, other_user):
        MemoryFact.objects.create(user=user, fact_text='Prefers tea')
        MemoryFact.objects.create(user=other_user, fact_text='Prefers coffee')

        response = auth_client.get(reverse('ai-memory-list'))

        assert response.status_code == 200
        facts = [f['fact_text'] for f in response.json()]
        assert facts == ['Prefers tea']

    def test_response_includes_category(self, auth_client, user):
        from apps.ai_companion.models import MemoryCategory

        MemoryFact.objects.create(user=user, fact_text='Prefers tea', category=MemoryCategory.PREFERENCE)

        response = auth_client.get(reverse('ai-memory-list'))

        assert response.status_code == 200
        assert response.json()[0]['category'] == 'preference'

    def test_filters_by_category(self, auth_client, user):
        from apps.ai_companion.models import MemoryCategory

        MemoryFact.objects.create(user=user, fact_text='Prefers tea', category=MemoryCategory.PREFERENCE)
        MemoryFact.objects.create(user=user, fact_text='Is a teacher', category=MemoryCategory.PERSONAL_FACT)

        response = auth_client.get(reverse('ai-memory-list'), {'category': 'preference'})

        assert response.status_code == 200
        facts = [f['fact_text'] for f in response.json()]
        assert facts == ['Prefers tea']

    def test_rejects_invalid_category(self, auth_client):
        response = auth_client.get(reverse('ai-memory-list'), {'category': 'not-a-real-category'})
        assert response.status_code == 400

    def test_excludes_deleted_facts(self, auth_client, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')
        fact.is_active = False
        fact.save(update_fields=['is_active'])

        response = auth_client.get(reverse('ai-memory-list'))

        assert response.status_code == 200
        assert response.json() == []


class TestMemoryFactDetailView:
    def test_requires_authentication(self, api_client, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')
        response = api_client.get(reverse('ai-memory-detail', kwargs={'fact_id': fact.id}))
        assert response.status_code == 401

    def test_retrieve_own_memory_fact(self, auth_client, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')

        response = auth_client.get(reverse('ai-memory-detail', kwargs={'fact_id': fact.id}))

        assert response.status_code == 200
        assert response.json()['fact_text'] == 'Prefers tea'

    def test_retrieve_missing_fact_returns_404(self, auth_client):
        response = auth_client.get(reverse('ai-memory-detail', kwargs={'fact_id': uuid.uuid4()}))
        assert response.status_code == 404

    def test_retrieve_other_users_fact_returns_404(self, auth_client, other_user):
        foreign = MemoryFact.objects.create(user=other_user, fact_text='Not mine')
        response = auth_client.get(reverse('ai-memory-detail', kwargs={'fact_id': foreign.id}))
        assert response.status_code == 404

    def test_edit_own_memory_fact(self, auth_client, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')

        response = auth_client.patch(
            reverse('ai-memory-detail', kwargs={'fact_id': fact.id}),
            {'fact_text': 'Prefers green tea', 'category': 'preference'},
            format='json',
        )

        assert response.status_code == 200
        body = response.json()
        assert body['fact_text'] == 'Prefers green tea'
        assert body['category'] == 'preference'

    def test_edit_rejects_blank_text(self, auth_client, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')

        response = auth_client.patch(
            reverse('ai-memory-detail', kwargs={'fact_id': fact.id}),
            {'fact_text': '   '},
            format='json',
        )

        assert response.status_code == 400

    def test_edit_rejects_duplicate_text(self, auth_client, user):
        MemoryFact.objects.create(user=user, fact_text='Prefers tea')
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers coffee')

        response = auth_client.patch(
            reverse('ai-memory-detail', kwargs={'fact_id': fact.id}),
            {'fact_text': 'Prefers tea'},
            format='json',
        )

        assert response.status_code == 409

    def test_edit_other_users_fact_returns_404(self, auth_client, other_user):
        foreign = MemoryFact.objects.create(user=other_user, fact_text='Not mine')

        response = auth_client.patch(
            reverse('ai-memory-detail', kwargs={'fact_id': foreign.id}),
            {'fact_text': 'Hijacked'},
            format='json',
        )

        assert response.status_code == 404

    def test_delete_own_memory_fact(self, auth_client, user):
        fact = MemoryFact.objects.create(user=user, fact_text='Prefers tea')

        response = auth_client.delete(reverse('ai-memory-detail', kwargs={'fact_id': fact.id}))

        assert response.status_code == 204
        fact.refresh_from_db()
        assert fact.is_active is False

    def test_delete_other_users_fact_returns_404(self, auth_client, other_user):
        foreign = MemoryFact.objects.create(user=other_user, fact_text='Not mine')

        response = auth_client.delete(reverse('ai-memory-detail', kwargs={'fact_id': foreign.id}))

        assert response.status_code == 404
