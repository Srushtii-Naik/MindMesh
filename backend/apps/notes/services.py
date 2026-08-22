"""
Service layer — Notes.

Domain business logic for categories, tags, notes, attachments, search, and
AI summaries. Per ARCHITECTURE.md Section 3: views call services; services
never import DRF. AI summarization goes through apps.ai_companion.services
(a service-layer entry point, not a direct model import), per
ARCHITECTURE.md Section 3's cross-domain communication rule — mirroring how
apps.calendar_events.services calls apps.tasks.services.get_tasks_due_between.
"""

from typing import BinaryIO

from django.conf import settings
from django.utils import timezone

from apps.accounts.models import User
from apps.ai_companion.services import SummarizationError, summarize_text
from apps.notes.models import Attachment, Category, Note, Tag
from apps.notes.repositories import (
    category_name_exists_for_user,
    count_notes_created_between,
    create_attachment,
    create_category,
    create_note,
    create_tag,
    delete_attachment,
    delete_category,
    delete_tag,
    get_attachment_for_note,
    get_category_for_user,
    get_note_for_user,
    get_tag_for_user,
    get_tags_for_user_by_ids,
    list_attachments_for_note,
    list_categories_for_user,
    list_notes_for_user,
    list_tags_for_user,
    search_notes,
    soft_delete_note,
    tag_name_exists_for_user,
    update_category,
    update_note,
)


class CategoryNotFoundError(Exception):
    """Raised when a category cannot be found for the requesting user."""


class CategoryNameAlreadyExistsError(Exception):
    """Raised when creating/renaming a category to a name the user already has."""


class TagNotFoundError(Exception):
    """Raised when a tag cannot be found for the requesting user."""


class TagNameAlreadyExistsError(Exception):
    """Raised when creating a tag with a name the user already has."""


class NoteNotFoundError(Exception):
    """Raised when a note cannot be found for the requesting user."""


class AttachmentNotFoundError(Exception):
    """Raised when an attachment cannot be found under the requesting user's note."""


class AttachmentTooLargeError(Exception):
    """Raised when an uploaded attachment exceeds NOTE_ATTACHMENT_MAX_SIZE_BYTES."""


class AttachmentTypeNotAllowedError(Exception):
    """Raised when an uploaded attachment's content type isn't allow-listed."""


class NoteSummaryError(Exception):
    """Raised when an AI summary cannot be generated for a note."""


# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------


def list_categories(user: User):
    return list_categories_for_user(user)


def create_category_for_user(user: User, *, name: str, color: str) -> Category:
    name = name.strip()
    if category_name_exists_for_user(user, name):
        raise CategoryNameAlreadyExistsError(f'You already have a category named "{name}".')
    return create_category(user=user, name=name, color=color)


def update_category_for_user(user: User, category_id, **fields) -> Category:
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')

    if 'name' in fields:
        name = fields['name'].strip()
        if category_name_exists_for_user(user, name, exclude_id=category.id):
            raise CategoryNameAlreadyExistsError(f'You already have a category named "{name}".')
        fields['name'] = name

    return update_category(category, **fields)


def delete_category_for_user(user: User, category_id) -> None:
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')
    delete_category(category)


def get_category(user: User, category_id) -> Category:
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')
    return category


def _resolve_category(user: User, category_id) -> Category | None:
    if category_id is None:
        return None
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')
    return category


# --------------------------------------------------------------------------
# Tags
# --------------------------------------------------------------------------


def list_tags(user: User):
    return list_tags_for_user(user)


def create_tag_for_user(user: User, *, name: str) -> Tag:
    name = name.strip()
    if tag_name_exists_for_user(user, name):
        raise TagNameAlreadyExistsError(f'You already have a tag named "{name}".')
    return create_tag(user=user, name=name)


def delete_tag_for_user(user: User, tag_id) -> None:
    tag = get_tag_for_user(user, tag_id)
    if tag is None:
        raise TagNotFoundError('Tag not found.')
    delete_tag(tag)


def get_tag(user: User, tag_id) -> Tag:
    tag = get_tag_for_user(user, tag_id)
    if tag is None:
        raise TagNotFoundError('Tag not found.')
    return tag


def _resolve_tags(user: User, tag_ids) -> list[Tag]:
    if not tag_ids:
        return []
    tags = list(get_tags_for_user_by_ids(user, tag_ids))
    found_ids = {str(tag.id) for tag in tags}
    missing = [str(tag_id) for tag_id in tag_ids if str(tag_id) not in found_ids]
    if missing:
        raise TagNotFoundError(f'Tag(s) not found: {", ".join(missing)}.')
    return tags


# --------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------


def list_notes_for_user_filtered(
    user: User,
    *,
    category_id=None,
    tag_id=None,
    search: str | None = None,
):
    """
    Filterable, searchable note listing (ROADMAP.md Milestone 6: "Categories
    and tags functional and filterable" / "Search returns accurate,
    performant results").
    """
    queryset = list_notes_for_user(user)

    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if tag_id:
        queryset = queryset.filter(tags__id=tag_id)
    if search:
        queryset = search_notes(queryset, search)

    return queryset.distinct()


def create_note_for_user(
    user: User,
    *,
    title: str,
    content: str = '',
    category_id=None,
    tag_ids: list | None = None,
) -> Note:
    category = _resolve_category(user, category_id)
    tags = _resolve_tags(user, tag_ids)

    return create_note(
        user=user,
        title=title.strip(),
        content=content,
        category=category,
        tags=tags,
    )


def update_note_for_user(user: User, note_id, **fields) -> Note:
    note = get_note_for_user(user, note_id)
    if note is None:
        raise NoteNotFoundError('Note not found.')

    tags_provided = 'tag_ids' in fields
    tags = _resolve_tags(user, fields.pop('tag_ids', None)) if tags_provided else None

    if 'category_id' in fields:
        fields['category'] = _resolve_category(user, fields.pop('category_id'))
    if 'title' in fields:
        fields['title'] = fields['title'].strip()

    return update_note(note, tags=tags, tags_provided=tags_provided, **fields)


def delete_note_for_user(user: User, note_id) -> None:
    note = get_note_for_user(user, note_id)
    if note is None:
        raise NoteNotFoundError('Note not found.')
    soft_delete_note(note)


def get_note(user: User, note_id) -> Note:
    note = get_note_for_user(user, note_id)
    if note is None:
        raise NoteNotFoundError('Note not found.')
    return note


def _get_owned_note(user: User, note_id) -> Note:
    note = get_note_for_user(user, note_id)
    if note is None:
        raise NoteNotFoundError('Note not found.')
    return note


# --------------------------------------------------------------------------
# Attachments
# --------------------------------------------------------------------------


def list_attachments_for_user_note(user: User, note_id):
    note = _get_owned_note(user, note_id)
    return list_attachments_for_note(note)


def add_attachment_for_user_note(user: User, note_id, uploaded_file: BinaryIO) -> Attachment:
    """
    Validates size and content type before persisting
    (ROADMAP.md Milestone 6: "Attachments upload/storage implemented securely").
    """
    note = _get_owned_note(user, note_id)

    max_size = settings.NOTE_ATTACHMENT_MAX_SIZE_BYTES
    if uploaded_file.size > max_size:
        raise AttachmentTooLargeError(
            f'File is too large. The maximum size is {max_size // (1024 * 1024)}MB.'
        )

    content_type = uploaded_file.content_type or 'application/octet-stream'
    if content_type not in settings.NOTE_ATTACHMENT_ALLOWED_CONTENT_TYPES:
        raise AttachmentTypeNotAllowedError(f'Files of type "{content_type}" are not allowed.')

    return create_attachment(
        note=note,
        file=uploaded_file,
        original_filename=uploaded_file.name,
        content_type=content_type,
        size_bytes=uploaded_file.size,
    )


def get_attachment_for_user_note(user: User, note_id, attachment_id) -> Attachment:
    note = _get_owned_note(user, note_id)
    attachment = get_attachment_for_note(note, attachment_id)
    if attachment is None:
        raise AttachmentNotFoundError('Attachment not found.')
    return attachment


def delete_attachment_for_user_note(user: User, note_id, attachment_id) -> None:
    attachment = get_attachment_for_user_note(user, note_id, attachment_id)
    delete_attachment(attachment)


# --------------------------------------------------------------------------
# AI summaries (basic implementation per ROADMAP.md Milestone 6; refined in
# Milestone 7 once the full AI Companion/context-assembly service exists)
# --------------------------------------------------------------------------


def generate_summary_for_user_note(user: User, note_id) -> Note:
    note = _get_owned_note(user, note_id)

    try:
        summary = summarize_text(note.content)
    except SummarizationError as exc:
        raise NoteSummaryError(str(exc)) from exc

    return update_note(note, ai_summary=summary, ai_summary_generated_at=timezone.now())


# --------------------------------------------------------------------------
# Cross-domain entry point for apps.analytics (ROADMAP.md Milestone 11) —
# never exposes the Note model itself, per ARCHITECTURE.md Section 3.
# --------------------------------------------------------------------------


def get_note_count_for_range(user: User, start_date, end_date) -> int:
    return count_notes_created_between(user, start_date, end_date)
