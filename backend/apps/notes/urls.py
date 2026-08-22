"""
URL routes — Notes.

Mounted at /api/v1/notes/ from config/urls.py, per ARCHITECTURE.md Section 6
API versioning convention.
"""

from django.urls import path

from apps.notes.views import (
    CategoryDetailView,
    CategoryListCreateView,
    NoteAttachmentDetailView,
    NoteAttachmentDownloadView,
    NoteAttachmentListCreateView,
    NoteDetailView,
    NoteListCreateView,
    NoteSummaryView,
    TagDetailView,
    TagListCreateView,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='note-category-list'),
    path('categories/<uuid:category_id>/', CategoryDetailView.as_view(), name='note-category-detail'),

    # Tags
    path('tags/', TagListCreateView.as_view(), name='note-tag-list'),
    path('tags/<uuid:tag_id>/', TagDetailView.as_view(), name='note-tag-detail'),

    # Notes
    path('', NoteListCreateView.as_view(), name='note-list'),
    path('<uuid:note_id>/', NoteDetailView.as_view(), name='note-detail'),
    path('<uuid:note_id>/summary/', NoteSummaryView.as_view(), name='note-summary'),

    # Attachments
    path('<uuid:note_id>/attachments/', NoteAttachmentListCreateView.as_view(), name='note-attachment-list'),
    path(
        '<uuid:note_id>/attachments/<uuid:attachment_id>/',
        NoteAttachmentDetailView.as_view(),
        name='note-attachment-detail',
    ),
    path(
        '<uuid:note_id>/attachments/<uuid:attachment_id>/download/',
        NoteAttachmentDownloadView.as_view(),
        name='note-attachment-download',
    ),
]
