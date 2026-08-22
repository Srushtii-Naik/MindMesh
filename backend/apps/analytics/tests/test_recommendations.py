"""Tests for apps.analytics.services.get_ai_recommendations (ROADMAP.md
Milestone 11: "AI-generated recommendations surfaced through the AI
abstraction layer"). Uses the default StubProvider (config/settings/test.py
AI_PROVIDER=stub) except where a specific provider response/failure is
simulated via monkeypatch, mirroring apps/ai_companion/tests/test_services.py.
"""

import pytest

from apps.analytics.services import get_ai_recommendations

pytestmark = pytest.mark.django_db


class TestAIRecommendations:
    def test_returns_a_non_empty_list_via_stub_provider(self, user):
        recommendations = get_ai_recommendations(user, use_cache=False)

        assert isinstance(recommendations, list)
        assert len(recommendations) >= 1
        assert all(isinstance(item, str) and item.strip() for item in recommendations)

    def test_degrades_to_empty_list_on_provider_failure(self, user, monkeypatch):
        from apps.ai_companion import services as ai_services
        from apps.ai_companion.providers import AIProviderError

        class _FailingProvider:
            def generate_response(self, *args, **kwargs):
                raise AIProviderError('provider unavailable')

        monkeypatch.setattr(ai_services, 'get_ai_provider', lambda: _FailingProvider())

        recommendations = get_ai_recommendations(user, use_cache=False)

        assert recommendations == []

    def test_splits_multiline_response_into_separate_recommendations(self, user, monkeypatch):
        from apps.ai_companion import services as ai_services

        class _MultilineProvider:
            def generate_response(self, *args, **kwargs):
                return 'Finish the overdue report.\nTake a short break today.\nPlan tomorrow.'

        monkeypatch.setattr(ai_services, 'get_ai_provider', lambda: _MultilineProvider())

        recommendations = get_ai_recommendations(user, use_cache=False)

        assert len(recommendations) == 3
        assert 'Finish the overdue report.' in recommendations

    def test_caches_recommendations_between_calls(self, user, monkeypatch):
        from apps.ai_companion import services as ai_services

        call_count = {'n': 0}

        class _CountingProvider:
            def generate_response(self, *args, **kwargs):
                call_count['n'] += 1
                return 'Keep up the good work.'

        monkeypatch.setattr(ai_services, 'get_ai_provider', lambda: _CountingProvider())

        first = get_ai_recommendations(user, use_cache=True)
        second = get_ai_recommendations(user, use_cache=True)

        assert first == second
        assert call_count['n'] == 1

    def test_recommendation_prompt_never_includes_raw_task_titles(self, user, monkeypatch):
        """PROJECT_RULES.md Section 10 ('Privacy-first AI... scoped and
        minimized'): the digest sent to the provider is a compact summary,
        not a data dump of the user's actual task content."""
        from apps.ai_companion import services as ai_services
        from apps.tasks.models import Task

        Task.objects.create(user=user, title='Confidential salary negotiation notes')

        captured = {}

        class _CapturingProvider:
            def generate_response(self, messages, *, context=''):
                captured['context'] = context
                return 'Stay on top of your tasks.'

        monkeypatch.setattr(ai_services, 'get_ai_provider', lambda: _CapturingProvider())

        get_ai_recommendations(user, use_cache=False)

        assert 'Confidential salary negotiation notes' not in captured['context']
