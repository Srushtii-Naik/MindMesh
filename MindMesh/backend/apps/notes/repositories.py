"""
Repository / data-access layer — Notes.

Encapsulates ORM queries for Note, Category, Tag, and Attachment, isolating
persistence details from the service layer, per ARCHITECTURE.md Section 3.
Every query here is scoped to a given user — row-level ownership per
PROJECT_RULES.md Section 7.
"""

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.notes.models import Attachment, Category, Note, Tag

# --------------------------------------------------------------------------
# Category
# --------------------------------------------------------------------------


def list_categories_for_user(user: User) -> QuerySet[Category]:
    return Category.objects.filter(user=user)


def get_category_for_user(user: User, category_id) -> Category | None:
    return Category.objects.filter(user=user, id=category_id).first()


def create_category(*, user: User, name: str, color: str) -> Category:
    return Category.objects.create(user=user, name=name, color=color)


def update_category(category: Category, **fields) -> Category:
    for field, value in fields.items():
        setattr(category, field, value)
    category.save()
    return category


def delete_category(category: Category) -> None:
    category.delete()


def category_name_exists_for_user(user: User, name: str, *, exclude_id=None) -> bool:
    qs = Category.objects.filter(user=user, name__iexact=name)
    if exclude_id is not None:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


# --------------------------------------------------------------------------
# Tag
# --------------------------------------------------------------------------


def list_tags_for_user(user: User) -> QuerySet[Tag]:
    return Tag.objects.filter(user=user)


def get_tag_for_user(user: User, tag_id) -> Tag | None:
    return Tag.objects.filter(user=user, id=tag_id).first()


def get_tags_for_user_by_ids(user: User, tag_ids: list) -> QuerySet[Tag]:
    return Tag.objects.filter(user=user, id__in=tag_ids)


def create_tag(*, user: User, name: str) -> Tag:
    return Tag.objects.create(user=user, name=name)


def delete_tag(tag: Tag) -> None:
    tag.delete()


def tag_name_exists_for_user(user: User, name: str) -> bool:
    return Tag.objects.filter(user=user, name__iexact=name).exists()


def get_tag_by_name_for_user(user: User, name: str) -> Tag | None:
    return Tag.objects.filter(user=user, name__iexact=name).first()


# --------------------------------------------------------------------------
# Note
# --------------------------------------------------------------------------


def list_notes_for_user(user: User) -> QuerySet[Note]:
    """Base queryset of the user's non-deleted notes. Filters applied by the service layer."""
    return (
        Note.objects.filter(user=user, is_active=True)
        .select_related('category')
        .prefetch_related('tags', 'attachments')
    )


def get_note_for_user(user: User, note_id) -> Note | None:
    return (
        Note.objects.filter(user=user, id=note_id, is_active=True)
        .select_related('category')
        .prefetch_related('tags', 'attachments')
        .first()
    )


def create_note(*, user: User, tags=None, **fields) -> Note:
    note = Note.objects.create(user=user, **fields)
    if tags:
        note.tags.set(tags)
    return note


def update_note(note: Note, *, tags=None, tags_provided: bool = False, **fields) -> Note:
    for field, value in fields.items():
        setattr(note, field, value)
    note.save()
    if tags_provided:
        note.tags.set(tags or [])
    return note


def soft_delete_note(note: Note) -> None:
    note.is_active = False
    note.deleted_at = timezone.now()
    note.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


def search_notes(queryset: QuerySet[Note], search: str) -> QuerySet[Note]:
    """Case-insensitive search across title and content, mirroring
    apps.tasks.services' title__icontains approach (ROADMAP.md Milestone 6:
    "Search returns accurate, performant results")."""
    return queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))


# --------------------------------------------------------------------------
# Attachment
# --------------------------------------------------------------------------


def list_attachments_for_note(note: Note) -> QuerySet[Attachment]:
    return Attachment.objects.filter(note=note)


def get_attachment_for_note(note: Note, attachment_id) -> Attachment | None:
    return Attachment.objects.filter(note=note, id=attachment_id).first()


def create_attachment(*, note: Note, **fields) -> Attachment:
    return Attachment.objects.create(note=note, **fields)


def delete_attachment(attachment: Attachment) -> None:
    # Removes the underlying file from storage, then the row itself — see
    # models.py docstring for why attachments are hard- rather than
    # soft-deleted.
    attachment.file.delete(save=False)
    attachment.delete()
