"""
AI Provider Abstraction Layer (ARCHITECTURE.md Section 7).

Defines the provider-agnostic contract that all domain code depends on, plus
concrete adapters for the supported vendors. Per PROJECT_RULES.md Section 10
("Never call providers directly... Always use the AI abstraction layer"),
this module is the *sole* egress point for calls to Gemini or OpenAI —
no other part of the backend imports their SDKs or calls their APIs.

Contract history: `summarize()` was brought forward in Milestone 6 to power
Notes' AI summaries. Milestone 7 (ROADMAP.md) completes the abstraction
contract described in ARCHITECTURE.md Section 7 with `generate_response`
(conversational replies) and `extract_memory` (durable-fact extraction),
per PROJECT_RULES.md Section 10's named contract methods. Adapters continue
to use the already-approved `requests` dependency via each vendor's plain
REST API rather than pulling in new SDK packages, per PROJECT_RULES.md
Section 2 (locked tech stack — no ad-hoc new dependencies).
"""

from __future__ import annotations

import abc
import logging
import re

import requests
from django.conf import settings

from apps.ai_companion.models import MemoryCategory

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Raised when a provider adapter fails to produce a response."""


class AIProvider(abc.ABC):
    """
    Provider-agnostic contract. Concrete adapters translate this into
    vendor-specific API calls; domain code (e.g. apps.notes.services,
    apps.ai_companion.services) only ever depends on this interface, never
    on a specific adapter.
    """

    @abc.abstractmethod
    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        """Return a short summary of `text`, at most `max_sentences` sentences."""
        raise NotImplementedError

    @abc.abstractmethod
    def generate_response(self, messages: list[dict], *, context: str = '') -> str:
        """
        Return a conversational reply given `messages` — an ordered list of
        `{"role": "user" | "assistant", "content": str}` dicts representing
        the conversation so far (oldest first) — and an optional `context`
        string assembled by the Context Assembly Service
        (apps.ai_companion.services.assemble_context_for_user) describing
        the user's relevant tasks/notes/calendar state.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def extract_memory(self, text: str) -> list[str]:
        """
        Return a list of short, durable fact strings worth remembering about
        the user, extracted from `text` (typically a single user message).
        Returns an empty list when nothing durable is present — most
        messages carry no memorable fact, and that's the expected case.
        """
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


# Simple, deterministic patterns for the foundational memory-extraction pass
# (ROADMAP.md Milestone 7: "Memory extraction — foundational; full engine in
# Milestone 8"). Intentionally conservative: only clear first-person
# declarations of a durable fact are captured, favoring precision over
# recall until Milestone 8's richer engine takes over. Used directly by
# StubProvider, and as the fallback for real adapters (mirrors
# _extractive_fallback's role for summarize()).
_MEMORY_FACT_PATTERNS = [
    re.compile(r"\bI(?:'m| am)\s+(?:a |an |the )?([^.!?\n]{3,80})", re.IGNORECASE),
    re.compile(r"\bmy\s+([^.!?\n]{3,80}?)\s+is\s+([^.!?\n]{1,80})", re.IGNORECASE),
    re.compile(r"\bI\s+(?:live|work)\s+(?:in|at)\s+([^.!?\n]{2,80})", re.IGNORECASE),
    re.compile(r"\bI\s+prefer\s+([^.!?\n]{3,80})", re.IGNORECASE),
    re.compile(r"\bI\s+(?:like|love|enjoy)\s+([^.!?\n]{3,80})", re.IGNORECASE),
]


def _heuristic_extract_memory(text: str) -> list[str]:
    """Deterministic, offline candidate-fact extraction shared by StubProvider
    and used as a fallback by the real adapters when a vendor call fails."""
    facts: list[str] = []
    for sentence in re.split(r'(?<=[.!?])\s+', text.strip()):
        sentence = sentence.strip().rstrip('.!?')
        if not sentence:
            continue
        for pattern in _MEMORY_FACT_PATTERNS:
            if pattern.search(sentence):
                fact = sentence[:1].upper() + sentence[1:]
                if fact not in facts:
                    facts.append(fact)
                break
    return facts


# Deterministic keyword buckets used to classify an already-extracted fact
# string into a MemoryCategory (ROADMAP.md Milestone 8: "User preferences,
# Important dates, Personal facts"). Kept as a plain module-level function
# rather than part of the AIProvider contract — it's local text
# classification, not a vendor call, so it applies identically regardless
# of which provider produced the fact text (PROJECT_RULES.md Section 10:
# domain logic "never assumes a specific vendor's... capability"). Checked
# in order; the first matching bucket wins, falling back to PERSONAL_FACT —
# the flat category every fact effectively had before this milestone.
_CATEGORY_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    (
        MemoryCategory.IMPORTANT_DATE,
        ('birthday', 'anniversary', 'due date', 'deadline', 'appointment', 'due on', 'scheduled for'),
    ),
    (
        MemoryCategory.RELATIONSHIP,
        (
            'my wife', 'my husband', 'my son', 'my daughter', 'my mother', 'my father',
            'my mom', 'my dad', 'my partner', 'my friend', 'my sister', 'my brother',
            'my spouse', 'my kids', 'my child',
        ),
    ),
    (
        MemoryCategory.ROUTINE,
        ('every day', 'every week', 'every morning', 'every night', 'daily', 'weekly', 'usually', 'routine'),
    ),
    (
        MemoryCategory.PREFERENCE,
        ('prefer', 'favorite', 'favourite', 'i like', 'i love', 'i enjoy', "don't like", 'i dislike', 'i hate'),
    ),
]


def categorize_memory_fact(fact_text: str) -> str:
    """Classify an extracted fact string into a `MemoryCategory` value.

    Used by apps.ai_companion.services when persisting a new MemoryFact, so
    categorization is applied consistently regardless of which provider
    (StubProvider, GeminiProvider, OpenAIProvider) produced the fact text.
    """
    lowered = (fact_text or '').lower()
    for category, keywords in _CATEGORY_KEYWORDS:
        if any(keyword in lowered for keyword in keywords):
            return category
    return MemoryCategory.PERSONAL_FACT


class StubProvider(AIProvider):
    """
    Deterministic, offline provider used whenever no vendor API key is
    configured (the default in development and always in tests). Produces
    naive-but-usable output for every contract method so the feature is
    fully usable and testable without network access or vendor credentials,
    while honoring the exact same interface a real adapter implements.
    """

    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        return _extractive_fallback(text, max_sentences=max_sentences)

    def generate_response(self, messages: list[dict], *, context: str = '') -> str:
        last_user_message = next(
            (m['content'] for m in reversed(messages) if m.get('role') == 'user'), ''
        )
        acknowledgement = last_user_message.strip() or "your message"
        if len(acknowledgement) > 160:
            acknowledgement = acknowledgement[:157].rstrip() + '...'

        if context.strip():
            return (
                f'Here\'s what I can tell you, based on what\'s going on for you right now: '
                f'{context.strip()} Regarding "{acknowledgement}" — I\'ve noted that.'
            )
        return f'I heard you say: "{acknowledgement}". How can I help with that?'

    def extract_memory(self, text: str) -> list[str]:
        return _heuristic_extract_memory(text)


class GeminiProvider(AIProvider):
    """Adapter for Google's Gemini API, called via its plain REST endpoint."""

    _ENDPOINT = (
        'https://generativelanguage.googleapis.com/v1beta/models/'
        'gemini-1.5-flash:generateContent'
    )

    def _call(self, prompt: str) -> str:
        api_key = getattr(settings, 'GEMINI_API_KEY', '') or ''
        if not api_key:
            raise AIProviderError('GEMINI_API_KEY is not configured.')

        response = requests.post(
            self._ENDPOINT,
            params={'key': api_key},
            json={'contents': [{'parts': [{'text': prompt}]}]},
            timeout=getattr(settings, 'AI_SUMMARY_TIMEOUT_SECONDS', 15),
        )
        response.raise_for_status()
        payload = response.json()
        return payload['candidates'][0]['content']['parts'][0]['text'].strip()

    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        prompt = (
            f'Summarize the following note in at most {max_sentences} sentences. '
            f'Respond with only the summary text, no preamble:\n\n{text}'
        )
        try:
            return self._call(prompt)
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('Gemini summarization failed, falling back to extractive summary: %s', exc)
            return _extractive_fallback(text, max_sentences=max_sentences)

    def generate_response(self, messages: list[dict], *, context: str = '') -> str:
        transcript = '\n'.join(f'{m["role"]}: {m["content"]}' for m in messages)
        context_block = f'Relevant context about the user:\n{context}\n\n' if context.strip() else ''
        prompt = (
            'You are MindMesh, a calm, trustworthy personal AI companion. '
            'Reply helpfully and concisely to the latest user message below, '
            'using the context only where relevant.\n\n'
            f'{context_block}Conversation so far:\n{transcript}\n\nassistant:'
        )
        try:
            return self._call(prompt)
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('Gemini chat response failed, falling back to stub reply: %s', exc)
            return StubProvider().generate_response(messages, context=context)

    def extract_memory(self, text: str) -> list[str]:
        prompt = (
            'Extract any durable, personal facts worth remembering long-term from the '
            'message below (preferences, routines, relationships, important dates). '
            'Respond with one short fact per line, no numbering, no preamble. '
            "If there's nothing durable, respond with exactly: none\n\n"
            f'Message:\n{text}'
        )
        try:
            raw = self._call(prompt)
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('Gemini memory extraction failed, falling back to heuristic extraction: %s', exc)
            return _heuristic_extract_memory(text)

        if raw.strip().lower() == 'none':
            return []
        return [line.strip('- ').strip() for line in raw.splitlines() if line.strip()]


class OpenAIProvider(AIProvider):
    """Adapter for OpenAI's Chat Completions API, called via its plain REST endpoint."""

    _ENDPOINT = 'https://api.openai.com/v1/chat/completions'

    def _call(self, prompt: str) -> str:
        api_key = getattr(settings, 'OPENAI_API_KEY', '') or ''
        if not api_key:
            raise AIProviderError('OPENAI_API_KEY is not configured.')

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
        return payload['choices'][0]['message']['content'].strip()

    def summarize(self, text: str, *, max_sentences: int = 3) -> str:
        prompt = (
            f'Summarize the following note in at most {max_sentences} sentences. '
            f'Respond with only the summary text, no preamble:\n\n{text}'
        )
        try:
            return self._call(prompt)
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('OpenAI summarization failed, falling back to extractive summary: %s', exc)
            return _extractive_fallback(text, max_sentences=max_sentences)

    def generate_response(self, messages: list[dict], *, context: str = '') -> str:
        transcript = '\n'.join(f'{m["role"]}: {m["content"]}' for m in messages)
        context_block = f'Relevant context about the user:\n{context}\n\n' if context.strip() else ''
        prompt = (
            'You are MindMesh, a calm, trustworthy personal AI companion. '
            'Reply helpfully and concisely to the latest user message below, '
            'using the context only where relevant.\n\n'
            f'{context_block}Conversation so far:\n{transcript}\n\nassistant:'
        )
        try:
            return self._call(prompt)
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('OpenAI chat response failed, falling back to stub reply: %s', exc)
            return StubProvider().generate_response(messages, context=context)

    def extract_memory(self, text: str) -> list[str]:
        prompt = (
            'Extract any durable, personal facts worth remembering long-term from the '
            'message below (preferences, routines, relationships, important dates). '
            'Respond with one short fact per line, no numbering, no preamble. '
            "If there's nothing durable, respond with exactly: none\n\n"
            f'Message:\n{text}'
        )
        try:
            raw = self._call(prompt)
        except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
            logger.warning('OpenAI memory extraction failed, falling back to heuristic extraction: %s', exc)
            return _heuristic_extract_memory(text)

        if raw.strip().lower() == 'none':
            return []
        return [line.strip('- ').strip() for line in raw.splitlines() if line.strip()]


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
