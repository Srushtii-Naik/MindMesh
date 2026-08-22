"""
Domain models — AI Companion (ROADMAP.md Milestone 7).

Per ARCHITECTURE.md Section 4: every domain table is scoped to a user_id
with row-level ownership enforced at the service layer, and timestamps are
standardized across all tables.

`Conversation` is user-generated content, so it uses soft deletes per
PROJECT_RULES.md Section 7 — mirroring apps.notes.Note. `Message` is
immutable once written (a chat transcript entry, not editable content), so
it is hard-deleted along with its conversation (CASCADE) rather than
soft-deleted — mirroring apps.notes.Attachment's reasoning for immutable
child records.

`MemoryFact` started as the *foundational* long-term memory store built in
Milestone 7 (a fact string plus provenance, per that milestone's completion
checklist: "Memory extraction logic captures durable facts — storage
refined in Milestone 8"). ROADMAP.md Milestone 8 ("Memory Engine") refines
it into MindMesh's durable memory record:

- `category` classifies each fact into the buckets ARCHITECTURE.md Section 7
  names for the Memory Manager ("preferences, recurring commitments,
  important dates") plus the general personal-fact/relationship buckets
  PRD.md Section 11 describes — captured via
  `apps.ai_companion.providers.categorize_memory_fact`.
- `is_active` / `deleted_at` make MemoryFact user-manageable content, soft
  deleted like `Conversation` above, since PRD.md Section 13 requires users
  be able to "view, edit, or delete stored memory at any time."
- `updated_at` is added now that facts are user-editable, not just
  AI-appended.

Deliberately still a flat fact string rather than a structured schema with
dedicated columns per category (e.g. a separate `important_date` date
field) — `category` + `fact_text` covers Milestone 8's scope without
guessing at a richer schema no feature yet needs (PROJECT_RULES.md Section
1: "When in doubt, leave it out"). Future embedding-based retrieval
(ARCHITECTURE.md Section 4/7 RAG readiness) needs no rework of this table:
a `MemoryFactEmbedding` table can reference `MemoryFact.id` the same way
`Message` already references `Conversation.id`, kept behind
`apps.ai_companion.repositories` so domain code never notices the change —
exactly the pattern ARCHITECTURE.md Section 4 describes for embeddings.
"""

import uuid

from django.conf import settings
from django.db import models


class MessageRole(models.TextChoices):
    """Who authored a given message in a conversation."""

    USER = 'user', 'User'
    ASSISTANT = 'assistant', 'Assistant'


class Conversation(models.Model):
    """A single chat thread between a user and the AI companion."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations'
    )
    title = models.CharField(max_length=255, blank=True, default='')

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_companion_conversation'
        ordering = ['-updated_at']
        verbose_name = 'conversation'
        verbose_name_plural = 'conversations'
        indexes = [
            models.Index(fields=['user', 'is_active', 'updated_at']),
        ]

    def __str__(self) -> str:
        return self.title or f'Conversation {self.id}'


class Message(models.Model):
    """A single turn (user or assistant) within a conversation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    role = models.CharField(max_length=10, choices=MessageRole.choices)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_companion_message'
        ordering = ['created_at']
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self) -> str:
        preview = self.content[:40]
        return f'{self.role}: {preview}'


class MemoryCategory(models.TextChoices):
    """
    Buckets a `MemoryFact` can fall into (ROADMAP.md Milestone 8 features:
    "User preferences", "Important dates", "Personal facts"; extended with
    ROUTINE/RELATIONSHIP to match the fuller vocabulary ARCHITECTURE.md
    Section 7 and PRD.md Section 11 use — "preferences, routines,
    relationships, and important recurring context"). Assigned by
    `apps.ai_companion.providers.categorize_memory_fact`, never guessed at
    in the view or repository layers.
    """

    PREFERENCE = 'preference', 'Preference'
    IMPORTANT_DATE = 'important_date', 'Important date'
    ROUTINE = 'routine', 'Routine'
    RELATIONSHIP = 'relationship', 'Relationship'
    PERSONAL_FACT = 'personal_fact', 'Personal fact'


class MemoryFact(models.Model):
    """
    A durable fact the AI companion remembers about the user — MindMesh's
    long-term memory record (ROADMAP.md Milestone 8: "Long-term memory
    storage... AI recall"). Extracted automatically from conversations via
    `apps.ai_companion.services.extract_and_store_memory_from_message`, and
    user-manageable thereafter (view/edit/delete) per PRD.md Section 13.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_memory_facts'
    )
    fact_text = models.CharField(max_length=500)
    category = models.CharField(
        max_length=20, choices=MemoryCategory.choices, default=MemoryCategory.PERSONAL_FACT
    )

    source_conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='extracted_facts',
    )

    # Soft delete (PROJECT_RULES.md Section 7) — mirrors Conversation above,
    # now that facts are user-editable/deletable rather than append-only.
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_companion_memory_fact'
        ordering = ['-created_at']
        verbose_name = 'memory fact'
        verbose_name_plural = 'memory facts'
        indexes = [
            models.Index(fields=['user', 'is_active', 'created_at']),
            models.Index(fields=['user', 'category']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'fact_text'],
                condition=models.Q(is_active=True),
                name='unique_active_memory_fact_per_user',
            )
        ]

    def __str__(self) -> str:
        return self.fact_text
