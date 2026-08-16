"""
DRF views — AI Companion.

Handles HTTP concerns only (request parsing, status codes, response
shaping, pagination). Business logic is delegated to
apps.ai_companion.services, per ARCHITECTURE.md Section 3.
"""

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_companion.serializers import (
    AISuggestionSerializer,
    ConversationSerializer,
    ConversationWriteSerializer,
    MemoryFactSerializer,
    MessageSerializer,
    MessageWriteSerializer,
)
from apps.ai_companion.services import (
    ChatResponseError,
    ConversationNotFoundError,
    EmptyMessageError,
    create_conversation_for_user,
    delete_conversation_for_user,
    get_ai_enhanced_suggestions,
    get_conversation,
    list_conversations,
    list_memory_facts,
    list_messages,
    send_message_for_user,
)

# --------------------------------------------------------------------------
# Conversations
# --------------------------------------------------------------------------


class ConversationListCreateView(APIView):
    """
    GET  /api/v1/ai/conversations/ — list the user's conversations.
    POST /api/v1/ai/conversations/ — start a new conversation.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        conversations = list_conversations(request.user)
        return Response(ConversationSerializer(conversations, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = ConversationWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = create_conversation_for_user(request.user, **serializer.validated_data)
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)


class ConversationDetailView(APIView):
    """
    GET    /api/v1/ai/conversations/<id>/ — retrieve a conversation.
    DELETE /api/v1/ai/conversations/<id>/ — soft-delete a conversation.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, conversation_id) -> Response:
        try:
            conversation = get_conversation(request.user, conversation_id)
        except ConversationNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'conversation_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ConversationSerializer(conversation).data)

    def delete(self, request: Request, conversation_id) -> Response:
        try:
            delete_conversation_for_user(request.user, conversation_id)
        except ConversationNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'conversation_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Messages / Chat
# --------------------------------------------------------------------------


class MessageListCreateView(APIView):
    """
    GET  /api/v1/ai/conversations/<conversation_id>/messages/ — retrieve
         the conversation's history (ROADMAP.md Milestone 7: "Conversation
         history persisted and retrievable").
    POST /api/v1/ai/conversations/<conversation_id>/messages/ — send a
         message and receive the AI companion's reply, generated through
         the AI abstraction layer.
    """

    permission_classes = [IsAuthenticated]
    throttle_scope = 'ai_chat'

    pagination_class = PageNumberPagination

    def get(self, request: Request, conversation_id) -> Response:
        try:
            messages = list_messages(request.user, conversation_id)
        except ConversationNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'conversation_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request, view=self)
        serializer = MessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request, conversation_id) -> Response:
        serializer = MessageWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            assistant_message = send_message_for_user(
                request.user, conversation_id, **serializer.validated_data
            )
        except ConversationNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'conversation_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except EmptyMessageError as exc:
            return Response(
                {'detail': str(exc), 'code': 'empty_message'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ChatResponseError as exc:
            return Response(
                {'detail': str(exc), 'code': 'chat_response_failed'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(MessageSerializer(assistant_message).data, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------
# Suggestions & Memory
# --------------------------------------------------------------------------


class AISuggestionsView(APIView):
    """GET /api/v1/ai/suggestions/ — Milestone 4's rule-based task
    suggestions, extended with one AI-generated proactive suggestion."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        suggestions = get_ai_enhanced_suggestions(request.user)
        return Response(AISuggestionSerializer(suggestions, many=True).data)


class MemoryFactListView(APIView):
    """GET /api/v1/ai/memory/ — the user's extracted memory facts
    (read-only; view/edit/delete controls are Milestone 8 scope per
    ROADMAP.md's completion checklist for that milestone)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        facts = list_memory_facts(request.user)
        return Response(MemoryFactSerializer(facts, many=True).data)
