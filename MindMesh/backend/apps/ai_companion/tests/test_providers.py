"""Unit tests for the AI Provider Abstraction Layer (providers.py)."""

import pytest

from apps.ai_companion.providers import (
    AIProviderError,
    GeminiProvider,
    OpenAIProvider,
    StubProvider,
    get_ai_provider,
)


class TestStubProvider:
    def test_returns_first_sentences(self):
        provider = StubProvider()
        text = 'First sentence. Second sentence. Third sentence. Fourth sentence.'

        summary = provider.summarize(text, max_sentences=2)

        assert summary == 'First sentence. Second sentence.'

    def test_handles_text_shorter_than_requested_sentence_count(self):
        provider = StubProvider()
        summary = provider.summarize('Only one sentence here.', max_sentences=3)
        assert summary == 'Only one sentence here.'

    def test_handles_text_with_no_sentence_terminators(self):
        provider = StubProvider()
        summary = provider.summarize('no punctuation at all', max_sentences=3)
        assert summary == 'no punctuation at all'


class TestGeminiProvider:
    def test_raises_when_api_key_missing(self, settings):
        settings.GEMINI_API_KEY = ''
        provider = GeminiProvider()

        with pytest.raises(AIProviderError):
            provider.summarize('Some note content.')

    def test_falls_back_to_extractive_summary_on_request_failure(self, settings, monkeypatch):
        settings.GEMINI_API_KEY = 'fake-key'

        def _raise(*args, **kwargs):
            import requests

            raise requests.RequestException('network down')

        monkeypatch.setattr('apps.ai_companion.providers.requests.post', _raise)

        provider = GeminiProvider()
        summary = provider.summarize('First sentence. Second sentence.', max_sentences=1)

        assert summary == 'First sentence.'


class TestOpenAIProvider:
    def test_raises_when_api_key_missing(self, settings):
        settings.OPENAI_API_KEY = ''
        provider = OpenAIProvider()

        with pytest.raises(AIProviderError):
            provider.summarize('Some note content.')

    def test_falls_back_to_extractive_summary_on_malformed_response(self, settings, monkeypatch):
        settings.OPENAI_API_KEY = 'fake-key'

        class _FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {'unexpected': 'shape'}

        monkeypatch.setattr(
            'apps.ai_companion.providers.requests.post', lambda *a, **k: _FakeResponse()
        )

        provider = OpenAIProvider()
        summary = provider.summarize('First sentence. Second sentence.', max_sentences=1)

        assert summary == 'First sentence.'


class TestGetAIProvider:
    def test_defaults_to_stub_for_unknown_provider_name(self, settings):
        settings.AI_PROVIDER = 'not-a-real-provider'
        assert isinstance(get_ai_provider(), StubProvider)

    def test_resolves_gemini(self, settings):
        settings.AI_PROVIDER = 'gemini'
        assert isinstance(get_ai_provider(), GeminiProvider)

    def test_resolves_openai(self, settings):
        settings.AI_PROVIDER = 'openai'
        assert isinstance(get_ai_provider(), OpenAIProvider)
