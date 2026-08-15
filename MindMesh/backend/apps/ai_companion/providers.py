"""
AI Provider Abstraction Layer (ARCHITECTURE.md Section 7).

Defines the provider-agnostic contract that all domain code depends on, plus
concrete adapters for the supported vendors. Per PROJECT_RULES.md Section 10
("Never call providers directly... Always use the AI abstraction layer"),
this module is the *sole* egress point for calls to Gemini or OpenAI —
no other part of the backend imports their SDKs or calls their APIs.

Scope note: only `summarize()` is implemented here, brought forward minimally
from ROADMAP.md Milestone 7 to satisfy Milestone 6's checklist item ("AI
summaries wired through the AI abstraction layer — basic implementation;
refined in Milestone 7"). The full contract (`generate_response`,
`extract_memory`) and the richer Context Assembly Service arrive in
Milestone 7/8. Adapters use the already-approved `requests` dependency via
each vendor's plain REST API rather than pulling in new SDK packages, per
PROJECT_RULES.md Section 2 (locked tech stack — no ad-hoc new dependencies).
"""

from __future__ import annotations

import abc
import logging
import re

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Raised when a provider adapter fails to produce a response."""


class AIProvider(abc.ABC):
    """
    Provider-agnostic contract. Concrete adapters translate this into
    vendor-specific API calls; domain code (e.g. apps.notes.services) only
    ever depends on this interface, never on a specific adapter.
    """

    @abc.abstractmethod
    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        """Return a short summary of `text`, at most `max_sentences` sentences."""
        raise NotImplementedError


def _extractive_fallback(text: str, *, max_sentences: int) -> str:
    """
    A simple, deterministic extractive summary: the first `max_sentences`
    sentences of the source text. Used by StubProvider directly, and by the
    real adapters as a last-resort fallback if a vendor response can't be
    parsed — better to degrade gracefully than to surface a raw error for
    what is, at heart, a convenience feature.
    """
    sentences = [segment.strip() for segment in re.split(r'(?<=[.!?])\s+', text.strip()) if segment.strip()]
    if not sentences:
        return text.strip()
    return ' '.join(sentences[:max_sentences])


class StubProvider(AIProvider):
    """
    Deterministic, offline provider used whenever no vendor API key is
    configured (the default in development and always in tests). Produces a
    naive extractive summary so the feature is fully usable and testable
    without network access or vendor credentials, while honoring the exact
    same interface a real adapter implements.
    """

    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        return _extractive_fallback(text, max_sentences=max_sentences)


class GeminiProvider(AIProvider):
    """Adapter for Google's Gemini API, called via its plain REST endpoint."""

    _ENDPOINT = (
        'https://generativelanguage.googleapis.com/v1beta/models/'
        'gemini-1.5-flash:generateContent'
    )

    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        api_key = getattr(settings, 'GEMINI_API_KEY', '') or ''
        if not api_key:
            raise AIProviderError('GEMINI_API_KEY is not configured.')

        prompt = (
            f'Summarize the following note in at most {max_sentences} sentences. '
            f'Respond with only the summary text, no preamble:\n\n{text}'
        )

        try:
            response = requests.post(
                self._ENDPOINT,
                params={'key': api_key},
                json={'contents': [{'parts': [{'text': prompt}]}]},
                timeout=getattr(settings, 'AI_SUMMARY_TIMEOUT_SECONDS', 15),
            )
            response.raise_for_status()
            payload = response.json()
            summary = payload['candidates'][0]['content']['parts'][0]['text']
            return summary.strip()
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('Gemini summarization failed, falling back to extractive summary: %s', exc)
            return _extractive_fallback(text, max_sentences=max_sentences)


class OpenAIProvider(AIProvider):
    """Adapter for OpenAI's Chat Completions API, called via its plain REST endpoint."""

    _ENDPOINT = 'https://api.openai.com/v1/chat/completions'

    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        api_key = getattr(settings, 'OPENAI_API_KEY', '') or ''
        if not api_key:
            raise AIProviderError('OPENAI_API_KEY is not configured.')

        prompt = (
            f'Summarize the following note in at most {max_sentences} sentences. '
            f'Respond with only the summary text, no preamble:\n\n{text}'
        )

        try:
            response = requests.post(
                self._ENDPOINT,
                headers={'Authorization': f'Bearer {api_key}'},
                json={
                    'model': getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.3,
                },
                timeout=getattr(settings, 'AI_SUMMARY_TIMEOUT_SECONDS', 15),
            )
            response.raise_for_status()
            payload = response.json()
            summary = payload['choices'][0]['message']['content']
            return summary.strip()
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('OpenAI summarization failed, falling back to extractive summary: %s', exc)
            return _extractive_fallback(text, max_sentences=max_sentences)


_PROVIDERS: dict[str, type[AIProvider]] = {
    'stub': StubProvider,
    'gemini': GeminiProvider,
    'openai': OpenAIProvider,
}


def get_ai_provider() -> AIProvider:
    """
    Resolve the configured provider adapter (`AI_PROVIDER` setting, default
    `stub`). This is the one place that knows which vendor is active —
    swapping providers means changing this setting, never domain code, per
    ARCHITECTURE.md Section 7 ("Swapping or adding a provider requires only
    a new adapter, not changes to domain logic").
    """
    provider_name = getattr(settings, 'AI_PROVIDER', 'stub')
    provider_class = _PROVIDERS.get(provider_name, StubProvider)
    return provider_class()
