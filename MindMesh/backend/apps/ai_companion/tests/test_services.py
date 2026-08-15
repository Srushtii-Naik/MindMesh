"""Unit tests for apps.ai_companion.services — the cross-domain entry point
other apps (e.g. apps.notes) call into. Uses the default StubProvider
(config/settings/test.py sets AI_PROVIDER='stub') so these run fully offline.
"""

import pytest

from apps.ai_companion.services import SummarizationError, summarize_text


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
