"""
Domain models — Notes & Knowledge (ROADMAP.md Milestone 6).

Per ARCHITECTURE.md Section 4: every domain table is scoped to a user_id
with row-level ownership enforced at the service layer, and timestamps are
standardized across all tables. Note is user-generated content, so it uses
soft deletes per PROJECT_RULES.md Section 7 — mirroring apps.tasks.Task.
Category and Tag are lightweight labels rather than content in their own
right (same reasoning as apps.tasks.Category), so they're hard-deleted.
Attachment is real user content but has its own housekeeping/purge story
planned for ROADMAP.md Milestone 12 ("soft-deleted record purging"), so it's
hard-deleted here rather than duplicating that infrastructure early —
deleting the row also frees the underlying file (see repositories.py).
"""

import uuid

from django.conf import settings
from django.db import models


def note_attachment_upload_path(instance: 'Attachment', filename: str) -> str:
    """Namespaced by user id so uploaded filenames can't collide or be
    guessed across users; the actual download is always mediated by an
    authenticated, ownership-checked view (see views.py), never a public
    MEDIA_URL path."""
    return f'note_attachments/{instance.note.user_id}/{uuid.uuid4().hex}_{filename}'


class Category(models.Model):
    """A user-defined label for grouping notes, mirroring apps.tasks.Category."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='note_categories'
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#5f6dfa')  # brand-500

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notes_category'
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_note_category_name_per_user')
        ]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """A short, user-defined label a note can carry several of (many-to-many)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='note_tags'
    )
    name = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notes_tag'
        ordering = ['name']
        verbose_name = 'tag'
        verbose_name_plural = 'tags'
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_note_tag_name_per_user')
        ]

    def __str__(self) -> str:
        return self.name


class Note(models.Model):
    """
    A single note owned by a user.

    `content` holds lightweight, structured plain text (a constrained
    Markdown subset — headings, bold/italic, lists) per ROADMAP.md
    Milestone 6 ("Rich notes (formatted text)"). Rendering to on-screen
    formatting happens client-side (frontend/src/features/notes/markdown.ts)
    rather than via a stored HTML blob, so there is no server- or client-side
    HTML injection surface per PROJECT_RULES.md Section 8 ("XSS protection").

    `ai_summary`/`ai_summary_generated_at` cache the most recent AI-generated
    summary (Milestone 6: "AI summaries wired through the AI abstraction
    layer") so it doesn't need to be regenerated on every read.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes'
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, default='')

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')

    ai_summary = models.TextField(blank=True, default='')
    ai_summary_generated_at = models.DateTimeField(null=True, blank=True)

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notes_note'
        ordering = ['-updated_at']
        verbose_name = 'note'
        verbose_name_plural = 'notes'
        indexes = [
            models.Index(fields=['user', 'is_active', 'updated_at']),
            models.Index(fields=['user', 'is_active', 'title']),
        ]

    def __str__(self) -> str:
        return self.title


class Attachment(models.Model):
    """A file attached to a note (ROADMAP.md Milestone 6: "Attachments")."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=note_attachment_upload_path)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes_attachment'
        ordering = ['created_at']
        verbose_name = 'attachment'
        verbose_name_plural = 'attachments'

    def __str__(self) -> str:
        return self.original_filename
