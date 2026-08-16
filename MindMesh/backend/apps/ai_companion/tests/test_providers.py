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


class TestStubProviderGenerateResponse:
    def test_echoes_last_user_message_without_context(self):
        provider = StubProvider()
        messages = [{'role': 'user', 'content': 'What should I do today?'}]

        reply = provider.generate_response(messages, context='')

        assert 'What should I do today?' in reply

    def test_incorporates_context_when_present(self):
        provider = StubProvider()
        messages = [{'role': 'user', 'content': 'Any suggestions?'}]

        reply = provider.generate_response(messages, context='2 task(s) are due today.')

        assert '2 task(s) are due today.' in reply

    def test_handles_no_user_message_gracefully(self):
        provider = StubProvider()
        reply = provider.generate_response([], context='')
        assert isinstance(reply, str)
        assert reply != ''

    def test_truncates_very_long_user_message(self):
        provider = StubProvider()
        long_message = 'x' * 500
        reply = provider.generate_response([{'role': 'user', 'content': long_message}], context='')
        assert len(reply) < 500 + 100


class TestStubProviderExtractMemory:
    def test_extracts_first_person_identity_statement(self):
        provider = StubProvider()
        facts = provider.extract_memory('I am a nurse and I work night shifts.')
        assert any('nurse' in fact.lower() for fact in facts)

    def test_extracts_preference_statement(self):
        provider = StubProvider()
        facts = provider.extract_memory('I prefer tea over coffee in the mornings.')
        assert any('prefer' in fact.lower() for fact in facts)

    def test_returns_empty_list_for_non_factual_message(self):
        provider = StubProvider()
        facts = provider.extract_memory('What time is it?')
        assert facts == []

    def test_does_not_duplicate_facts_within_same_message(self):
        provider = StubProvider()
        facts = provider.extract_memory('I am a teacher. I am a teacher.')
        assert len(facts) == len(set(facts))


class TestGeminiProviderGenerateResponse:
    def test_raises_when_api_key_missing(self, settings):
        settings.GEMINI_API_KEY = ''
        provider = GeminiProvider()
        with pytest.raises(AIProviderError):
            provider.generate_response([{'role': 'user', 'content': 'hi'}], context='')

    def test_falls_back_to_stub_reply_on_request_failure(self, settings, monkeypatch):
        settings.GEMINI_API_KEY = 'fake-key'

        def _raise(*args, **kwargs):
            import requests

            raise requests.RequestException('network down')

        monkeypatch.setattr('apps.ai_companion.providers.requests.post', _raise)

        provider = GeminiProvider()
        reply = provider.generate_response([{'role': 'user', 'content': 'hello'}], context='')

        assert 'hello' in reply


class TestGeminiProviderExtractMemory:
    def test_raises_when_api_key_missing(self, settings):
        settings.GEMINI_API_KEY = ''
        provider = GeminiProvider()
        with pytest.raises(AIProviderError):
            provider.extract_memory('I live in Bengaluru.')

    def test_falls_back_to_heuristic_extraction_on_failure(self, settings, monkeypatch):
        settings.GEMINI_API_KEY = 'fake-key'

        def _raise(*args, **kwargs):
            import requests

            raise requests.RequestException('network down')

        monkeypatch.setattr('apps.ai_companion.providers.requests.post', _raise)

        provider = GeminiProvider()
        facts = provider.extract_memory('I live in Bengaluru.')

        assert any('bengaluru' in fact.lower() for fact in facts)

    def test_parses_none_response_as_empty_list(self, settings, monkeypatch):
        settings.GEMINI_API_KEY = 'fake-key'

        class _FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {'candidates': [{'content': {'parts': [{'text': 'none'}]}}]}

        monkeypatch.setattr(
            'apps.ai_companion.providers.requests.post', lambda *a, **k: _FakeResponse()
        )

        provider = GeminiProvider()
        assert provider.extract_memory('Just chatting.') == []


class TestOpenAIProviderGenerateResponse:
    def test_raises_when_api_key_missing(self, settings):
        settings.OPENAI_API_KEY = ''
        provider = OpenAIProvider()
        with pytest.raises(AIProviderError):
            provider.generate_response([{'role': 'user', 'content': 'hi'}], context='')

    def test_falls_back_to_stub_reply_on_malformed_response(self, settings, monkeypatch):
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
        reply = provider.generate_response([{'role': 'user', 'content': 'hello'}], context='')

        assert 'hello' in reply


class TestOpenAIProviderExtractMemory:
    def test_raises_when_api_key_missing(self, settings):
        settings.OPENAI_API_KEY = ''
        provider = OpenAIProvider()
        with pytest.raises(AIProviderError):
            provider.extract_memory('I live in Bengaluru.')

    def test_falls_back_to_heuristic_extraction_on_malformed_response(self, settings, monkeypatch):
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
        facts = provider.extract_memory('I live in Bengaluru.')

        assert any('bengaluru' in fact.lower() for fact in facts)
