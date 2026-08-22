"""
Service layer — AI Companion.

Per ARCHITECTURE.md Section 3: views call services; services never import
DRF. `summarize_text` remains the cross-domain entry point apps.notes calls
(Milestone 6). Milestone 7 added the conversational surface: conversations,
messages, the Context Assembly Service, memory extraction, and AI-enhanced
suggestions — all routed through apps.ai_companion.providers, the sole
egress point to Gemini/OpenAI (PROJECT_RULES.md Section 10). Milestone 8
("Memory Engine") refines memory extraction into a categorized, durable
store the user can view/edit/delete, and folds it back into the Context
Assembly Service's digest so recall demonstrably shapes later replies.

Context Assembly Service (ARCHITECTURE.md Section 7): before each AI call,
gathers relevant context from the user's other domains. Reads them only
through their own service-layer entry points — apps.tasks.services,
apps.calendar_events.services, apps.notes.services — never by importing
their models directly, mirroring how apps.calendar_events.services already
calls apps.tasks.services.get_tasks_due_between (ARCHITECTURE.md Section 3:
"cross-domain communication happens through service interfaces, not direct
model imports across apps"). Per PROJECT_RULES.md Section 10
("Privacy-first AI... scoped and minimized"), only a compact natural-
language digest is assembled — never a raw data dump — and it is the only
per-user data that ever leaves the abstraction layer's boundary to a
provider adapter.
"""

from __future__ import annotations

from django.utils import timezone

from apps.accounts.models import User
from apps.ai_companion.models import Conversation, MemoryCategory, MemoryFact, Message, MessageRole
from apps.ai_companion.providers import AIProviderError, categorize_memory_fact, get_ai_provider
from apps.ai_companion.repositories import (
    create_conversation,
    create_memory_fact,
    create_message,
    get_conversation_for_user,
    get_memory_fact_for_user,
    list_conversations_for_user,
    list_memory_facts_for_user,
    list_messages_for_conversation,
    memory_fact_exists_for_user,
    soft_delete_conversation,
    soft_delete_memory_fact,
    touch_conversation,
    update_conversation,
    update_memory_fact,
)

# Cross-domain entry points only (ARCHITECTURE.md Section 3) — never the
# other domains' models. apps.notes.services is imported lazily inside
# assemble_context_for_user() rather than here: apps.notes.services imports
# apps.ai_companion.services (for summarize_text) at module load time, so a
# top-level import here would create a circular import between the two
# modules. calendar_events and tasks don't import ai_companion, so no such
# cycle applies to them.
from apps.calendar_events.services import get_daily_planner
from apps.tasks.services import get_task_suggestions, get_today_summary

# Bounds on how much conversation history and context are sent to a
# provider per call — keeps requests fast, cheap, and privacy-minimal
# (PROJECT_RULES.md Section 10 & 11).
MAX_HISTORY_MESSAGES = 20
MAX_CONTEXT_NOTES = 3


class SummarizationError(Exception):
    """Raised when a summary cannot be produced for the given text."""


class ConversationNotFoundError(Exception):
    """Raised when a conversation cannot be found for the requesting user."""


class EmptyMessageError(Exception):
    """Raised when a chat message has no meaningful content."""


class ChatResponseError(Exception):
    """Raised when the AI provider cannot produce a chat response."""


class MemoryFactNotFoundError(Exception):
    """Raised when a memory fact cannot be found for the requesting user."""


class DuplicateMemoryFactError(Exception):
    """Raised when editing a fact's text would collide with another of the
    user's existing active facts."""


# --------------------------------------------------------------------------
# Summarization (Milestone 6 — unchanged cross-domain entry point)
# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------
# Context Assembly Service
# --------------------------------------------------------------------------


def assemble_context_for_user(user: User) -> str:
    """
    Builds a compact, natural-language digest of the user's current
    tasks/notes/calendar state for the AI provider to ground its replies in
    (ARCHITECTURE.md Section 7 — Context Assembly Service). Never includes
    raw IDs or unrelated fields — only what's relevant for a helpful,
    human-readable reply, per PROJECT_RULES.md Section 10.
    """
    lines: list[str] = []

    summary = get_today_summary(user)
    if summary['overdue_count']:
        lines.append(f"{summary['overdue_count']} task(s) are overdue.")
    if summary['due_today_count']:
        lines.append(f"{summary['due_today_count']} task(s) are due today.")

    today = timezone.localdate()
    planner = get_daily_planner(user, today)
    if planner['events']:
        event_titles = ', '.join(event.title for event in list(planner['events'])[:3])
        lines.append(f"Today's calendar includes: {event_titles}.")

    from apps.notes.services import list_notes_for_user_filtered

    recent_notes = list(list_notes_for_user_filtered(user)[:MAX_CONTEXT_NOTES])
    if recent_notes:
        note_titles = ', '.join(note.title for note in recent_notes)
        lines.append(f'Recently written notes: {note_titles}.')

    lines.extend(_describe_memory_facts(user))

    return ' '.join(lines)


# Cap on how many stored facts are digested into context per call — keeps
# the prompt small and privacy-minimal (PROJECT_RULES.md Section 10 & 11),
# while still covering every category the user has facts in.
MAX_CONTEXT_MEMORY_FACTS = 8

_MEMORY_CATEGORY_LABELS: dict[str, str] = {
    MemoryCategory.PREFERENCE: 'Preferences',
    MemoryCategory.IMPORTANT_DATE: 'Important dates',
    MemoryCategory.ROUTINE: 'Routines',
    MemoryCategory.RELATIONSHIP: 'Relationships',
    MemoryCategory.PERSONAL_FACT: 'Personal facts',
}


def _describe_memory_facts(user: User) -> list[str]:
    """
    Renders the user's stored MemoryFacts into a short, grouped digest for
    the Context Assembly Service (ROADMAP.md Milestone 8: "AI recall
    demonstrably influences responses in later sessions"). Grouping by
    category — rather than the flat "Known about the user: ..." line
    Milestone 7 used — lets the assistant weigh a preference differently
    from an important date without any change to the provider contract.
    """
    facts = list(list_memory_facts_for_user(user)[:MAX_CONTEXT_MEMORY_FACTS])
    if not facts:
        return []

    grouped: dict[str, list[str]] = {}
    for fact in facts:
        grouped.setdefault(fact.category, []).append(fact.fact_text)

    return [
        f'{label}: {"; ".join(grouped[category])}.'
        for category, label in _MEMORY_CATEGORY_LABELS.items()
        if category in grouped
    ]


# --------------------------------------------------------------------------
# Conversations
# --------------------------------------------------------------------------


def list_conversations(user: User):
    return list_conversations_for_user(user)


def get_conversation(user: User, conversation_id) -> Conversation:
    conversation = get_conversation_for_user(user, conversation_id)
    if conversation is None:
        raise ConversationNotFoundError('Conversation not found.')
    return conversation


def create_conversation_for_user(user: User, *, title: str = '') -> Conversation:
    return create_conversation(user=user, title=title.strip())


def delete_conversation_for_user(user: User, conversation_id) -> None:
    conversation = get_conversation(user, conversation_id)
    soft_delete_conversation(conversation)


def _derive_title(first_message: str) -> str:
    title = first_message.strip().splitlines()[0]
    return title[:77] + '...' if len(title) > 80 else title


# --------------------------------------------------------------------------
# Messages / Chat
# --------------------------------------------------------------------------


def list_messages(user: User, conversation_id):
    conversation = get_conversation(user, conversation_id)
    return list_messages_for_conversation(conversation)


def send_message_for_user(user: User, conversation_id, *, content: str) -> Message:
    """
    The AI chat endpoint's core flow (ROADMAP.md Milestone 7: "AI chat
    functional end-to-end through the provider abstraction layer"):
    1. Persist the user's message.
    2. Assemble context (Context Assembly Service) and recent history.
    3. Generate a reply through the AI abstraction layer — never a direct
       provider call (PROJECT_RULES.md Section 10).
    4. Persist and return the assistant's reply.

    Memory extraction runs separately, asynchronously via Celery
    (apps.ai_companion.tasks.extract_memory_from_message_task), so it never
    adds latency to the chat response itself (PROJECT_RULES.md Section 11:
    "Celery for background jobs... never blocking the request-response
    cycle").
    """
    cleaned = (content or '').strip()
    if not cleaned:
        raise EmptyMessageError('Message content cannot be empty.')

    conversation = get_conversation(user, conversation_id)

    user_message = create_message(conversation=conversation, role=MessageRole.USER, content=cleaned)

    if not conversation.title:
        update_conversation(conversation, title=_derive_title(cleaned))

    history = list(list_messages_for_conversation(conversation).order_by('-created_at')[:MAX_HISTORY_MESSAGES])
    history.reverse()
    provider_messages = [{'role': message.role, 'content': message.content} for message in history]

    context = assemble_context_for_user(user)

    provider = get_ai_provider()
    try:
        reply_text = provider.generate_response(provider_messages, context=context)
    except AIProviderError as exc:
        raise ChatResponseError(str(exc)) from exc

    reply_text = (reply_text or '').strip()
    if not reply_text:
        raise ChatResponseError('The AI provider returned an empty response.')

    assistant_message = create_message(
        conversation=conversation, role=MessageRole.ASSISTANT, content=reply_text
    )
    touch_conversation(conversation)

    _enqueue_memory_extraction(user_id=user.id, conversation_id=conversation.id, message_id=user_message.id)

    return assistant_message


def _enqueue_memory_extraction(*, user_id, conversation_id, message_id) -> None:
    """Imported lazily to avoid a celery_app import at module load time in
    contexts (e.g. migrations) that don't need it."""
    from apps.ai_companion.tasks import extract_memory_from_message_task

    extract_memory_from_message_task.delay(str(user_id), str(conversation_id), str(message_id))


# --------------------------------------------------------------------------
# Memory extraction (foundational — ROADMAP.md Milestone 7; refined in 8)
# --------------------------------------------------------------------------


def extract_and_store_memory_from_message(user: User, conversation: Conversation, message: Message) -> list[MemoryFact]:
    """Runs the AI abstraction layer's `extract_memory` on a single message
    and persists any new, non-duplicate facts, each classified into a
    MemoryCategory via `apps.ai_companion.providers.categorize_memory_fact`
    (ROADMAP.md Milestone 8). Called from the Celery task
    (apps.ai_companion.tasks), never inline in the request/response cycle."""
    if message.role != MessageRole.USER:
        return []

    provider = get_ai_provider()
    try:
        candidate_facts = provider.extract_memory(message.content)
    except AIProviderError:
        return []

    created: list[MemoryFact] = []
    for fact_text in candidate_facts:
        fact_text = (fact_text or '').strip()
        if not fact_text or len(fact_text) > 500:
            continue
        if memory_fact_exists_for_user(user, fact_text):
            continue
        category = categorize_memory_fact(fact_text)
        created.append(
            create_memory_fact(
                user=user, fact_text=fact_text, category=category, source_conversation=conversation
            )
        )

    return created


def list_memory_facts(user: User, *, category: str | None = None):
    """The user's stored memory facts (ROADMAP.md Milestone 8: "User-facing
    controls to view... stored memory"), optionally filtered by category."""
    return list_memory_facts_for_user(user, category=category)


def get_memory_fact(user: User, fact_id) -> MemoryFact:
    fact = get_memory_fact_for_user(user, fact_id)
    if fact is None:
        raise MemoryFactNotFoundError('Memory fact not found.')
    return fact


def update_memory_fact_for_user(user: User, fact_id, **fields) -> MemoryFact:
    """Milestone 8: "User-facing controls to... edit... stored memory."
    Only `fact_text` and `category` are editable; provenance
    (`source_conversation`) is left untouched by a user edit."""
    fact = get_memory_fact(user, fact_id)

    if 'fact_text' in fields:
        fact_text = fields['fact_text'].strip()
        if memory_fact_exists_for_user(user, fact_text, exclude_id=fact.id):
            raise DuplicateMemoryFactError(f'You already have a memory fact saying "{fact_text}".')
        fields['fact_text'] = fact_text

    return update_memory_fact(fact, **fields)


def delete_memory_fact_for_user(user: User, fact_id) -> None:
    """Milestone 8: "User-facing controls to... delete stored memory" —
    the trust/privacy requirement from PRD.md Section 13."""
    fact = get_memory_fact(user, fact_id)
    soft_delete_memory_fact(fact)


# --------------------------------------------------------------------------
# AI-enhanced suggestions (ROADMAP.md Milestone 7 — builds on Milestone 4's
# rule-based apps.tasks.services.get_task_suggestions)
# --------------------------------------------------------------------------


def get_ai_enhanced_suggestions(user: User) -> list[dict]:
    """
    Extends Milestone 4's rule-based task suggestions with one proactive,
    natural-language suggestion synthesized across the user's current
    context — the "AI-enhanced" layer called for in ROADMAP.md Milestone 7,
    without duplicating the underlying rule logic (PROJECT_RULES.md Section
    3 — DRY). Degrades gracefully to the rule-based list alone if the AI
    provider is unavailable, since the baseline suggestions must never
    depend on AI availability.
    """
    suggestions = list(get_task_suggestions(user))
    if not suggestions:
        return suggestions

    context = assemble_context_for_user(user)
    if not context.strip():
        return suggestions

    provider = get_ai_provider()
    prompt_messages = [{
        'role': 'user',
        'content': (
            'In one short, encouraging sentence, help me prioritize what to focus on next.'
        ),
    }]
    try:
        proactive_message = provider.generate_response(prompt_messages, context=context)
    except AIProviderError:
        return suggestions

    proactive_message = (proactive_message or '').strip()
    if not proactive_message:
        return suggestions

    suggestions.append({
        'id': 'ai-proactive',
        'kind': 'ai_proactive',
        'message': proactive_message,
        'task_id': None,
    })
    return suggestions


# --------------------------------------------------------------------------
# Generic completion entry point (ROADMAP.md Milestone 11) — a thin wrapper
# around provider.generate_response for callers outside the chat surface
# (no Conversation/Message persistence, no chat history). Mirrors
# summarize_text's role as notes' cross-domain AI entry point, so
# apps.analytics reaches the AI abstraction layer through
# apps.ai_companion.services rather than apps.ai_companion.providers
# directly, per ARCHITECTURE.md Section 3.
# --------------------------------------------------------------------------


class RecommendationError(Exception):
    """Raised when the AI provider cannot produce recommendation text."""


def generate_recommendation_text(prompt: str, *, context: str = '') -> str:
    """Returns a single AI-generated reply for `prompt`, grounded in
    `context` (a compact digest assembled by the caller — never a raw data
    dump, per PROJECT_RULES.md Section 10)."""
    cleaned = (prompt or '').strip()
    if not cleaned:
        raise RecommendationError('Cannot generate a recommendation from an empty prompt.')

    provider = get_ai_provider()
    try:
        reply = provider.generate_response([{'role': 'user', 'content': cleaned}], context=context)
    except AIProviderError as exc:
        raise RecommendationError(str(exc)) from exc

    reply = (reply or '').strip()
    if not reply:
        raise RecommendationError('The AI provider returned an empty response.')
    return reply
