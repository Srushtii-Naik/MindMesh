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

`MemoryFact` is the *foundational* long-term memory store called for by this
milestone's completion checklist ("Memory extraction logic captures durable
facts — storage refined in Milestone 8"). It deliberately stays minimal —
a fact string plus provenance — since the richer memory engine (dedup,
categorization, embeddings/RAG-readiness per ARCHITECTURE.md Section 7) is
explicitly Milestone 8 scope. This mirrors how apps.reminders.Reminder
modeled just enough in Milestone 5 for Milestone 9 to build on later.
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


class MemoryFact(models.Model):
    """
    A durable fact extracted from the user's conversations
    (ROADMAP.md Milestone 7: "Memory extraction — foundational; full engine
    in Milestone 8"). Deliberately a flat fact string rather than a
    structured schema — Milestone 8 owns categorization, deduplication, and
    the embeddings-based recall path described in ARCHITECTURE.md Section 7.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_memory_facts'
    )
    fact_text = models.CharField(max_length=500)

    source_conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='extracted_facts',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_companion_memory_fact'
        ordering = ['-created_at']
        verbose_name = 'memory fact'
        verbose_name_plural = 'memory facts'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'fact_text'], name='unique_memory_fact_per_user')
        ]

    def __str__(self) -> str:
        return self.fact_text
