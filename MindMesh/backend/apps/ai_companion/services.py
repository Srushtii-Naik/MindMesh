"""
Service layer — AI Companion.

Per ARCHITECTURE.md Section 3: views call services; services never import
DRF. `summarize_text` is the cross-domain entry point other apps (e.g.
apps.notes) call — mirroring apps.tasks.services.get_tasks_due_between's
role for calendar_events — so no other domain ever imports
apps.ai_companion.providers directly, per ARCHITECTURE.md Section 3
("cross-domain communication happens through service interfaces, not
direct model imports across apps").

Scope note: full conversational features (chat, context assembly, memory
extraction) are built out in ROADMAP.md Milestones 7 and 8. This module
currently exposes only what Milestone 6 (Notes & Knowledge) needs.
"""

from apps.ai_companion.providers import AIProviderError, get_ai_provider


class SummarizationError(Exception):
    """Raised when a summary cannot be produced for the given text."""


def summarize_text(text: str, *, max_sentences: int = 3) -> str:
    """Summarize arbitrary text through the AI abstraction layer.

    Per PROJECT_RULES.md Section 10 ("Privacy-first AI... scoped and
    minimized"), callers should pass only the note content itself — never
    additional unrelated user data.
    """
    cleaned = (text or '').strip()
    if not cleaned:
        raise SummarizationError('Cannot summarize empty content.')

    provider = get_ai_provider()
    try:
        summary = provider.summarize(cleaned, max_sentences=max_sentences)
    except AIProviderError as exc:
        raise SummarizationError(str(exc)) from exc

    summary = (summary or '').strip()
    if not summary:
        raise SummarizationError('The AI provider returned an empty summary.')
    return summary
