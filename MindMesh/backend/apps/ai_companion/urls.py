"""
URL routes — AI Companion.

Mounted at /api/v1/ai/ from config/urls.py, per ARCHITECTURE.md Section 6
API versioning convention.
"""

from django.urls import path

from apps.ai_companion.views import (
    AISuggestionsView,
    ConversationDetailView,
    ConversationListCreateView,
    MemoryFactDetailView,
    MemoryFactListView,
    MessageListCreateView,
)

urlpatterns = [
    # Conversations
    path('conversations/', ConversationListCreateView.as_view(), name='ai-conversation-list'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='ai-conversation-detail'),

    # Messages / Chat
    path(
        'conversations/<uuid:conversation_id>/messages/',
        MessageListCreateView.as_view(),
        name='ai-message-list',
    ),

    # Suggestions & Memory
    path('suggestions/', AISuggestionsView.as_view(), name='ai-suggestions'),
    path('memory/', MemoryFactListView.as_view(), name='ai-memory-list'),
    path('memory/<uuid:fact_id>/', MemoryFactDetailView.as_view(), name='ai-memory-detail'),
]
