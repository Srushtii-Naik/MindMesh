"""
DRF views — Notes.

Handles HTTP concerns only (request parsing, status codes, response
shaping, pagination). Business logic is delegated to apps.notes.services,
per ARCHITECTURE.md Section 3.
"""

from django.http import FileResponse
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notes.serializers import (
    AttachmentSerializer,
    CategorySerializer,
    CategoryWriteSerializer,
    NoteFilterSerializer,
    NoteSerializer,
    NoteWriteSerializer,
    TagSerializer,
    TagWriteSerializer,
)
from apps.notes.services import (
    AttachmentNotFoundError,
    AttachmentTooLargeError,
    AttachmentTypeNotAllowedError,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    NoteNotFoundError,
    NoteSummaryError,
    TagNameAlreadyExistsError,
    TagNotFoundError,
    add_attachment_for_user_note,
    create_category_for_user,
    create_note_for_user,
    create_tag_for_user,
    delete_attachment_for_user_note,
    delete_category_for_user,
    delete_note_for_user,
    delete_tag_for_user,
    generate_summary_for_user_note,
    get_attachment_for_user_note,
    get_category,
    get_note,
    list_attachments_for_user_note,
    list_categories,
    list_notes_for_user_filtered,
    list_tags,
    update_category_for_user,
    update_note_for_user,
)

# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------


class CategoryListCreateView(APIView):
    """
    GET  /api/v1/notes/categories/ — list the user's note categories.
    POST /api/v1/notes/categories/ — create a category.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        categories = list_categories(request.user)
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CategoryWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            category = create_category_for_user(request.user, **serializer.validated_data)
        except CategoryNameAlreadyExistsError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_name_exists'},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    """
    GET    /api/v1/notes/categories/<id>/ — retrieve a category.
    PATCH  /api/v1/notes/categories/<id>/ — update a category.
    DELETE /api/v1/notes/categories/<id>/ — delete a category.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, category_id) -> Response:
        try:
            category = get_category(request.user, category_id)
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CategorySerializer(category).data)

    def patch(self, request: Request, category_id) -> Response:
        serializer = CategoryWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            category = update_category_for_user(
                request.user, category_id, **serializer.validated_data
            )
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CategoryNameAlreadyExistsError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_name_exists'},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(CategorySerializer(category).data)

    def delete(self, request: Request, category_id) -> Response:
        try:
            delete_category_for_user(request.user, category_id)
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Tags
# --------------------------------------------------------------------------


class TagListCreateView(APIView):
    """
    GET  /api/v1/notes/tags/ — list the user's tags.
    POST /api/v1/notes/tags/ — create a tag.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        tags = list_tags(request.user)
        return Response(TagSerializer(tags, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = TagWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tag = create_tag_for_user(request.user, **serializer.validated_data)
        except TagNameAlreadyExistsError as exc:
            return Response(
                {'detail': str(exc), 'code': 'tag_name_exists'},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(TagSerializer(tag).data, status=status.HTTP_201_CREATED)


class TagDetailView(APIView):
    """DELETE /api/v1/notes/tags/<id>/ — delete a tag."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, tag_id) -> Response:
        try:
            delete_tag_for_user(request.user, tag_id)
        except TagNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'tag_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------


class NoteListCreateView(APIView):
    """
    GET  /api/v1/notes/ — list the user's notes, filterable by
         category_id/tag_id/search (ROADMAP.md Milestone 6:
         "Categories and tags functional and filterable" /
         "Search returns accurate, performant results").
    POST /api/v1/notes/ — create a note.
    """

    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request: Request) -> Response:
        filters = NoteFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        filter_kwargs = dict(filters.validated_data)

        queryset = list_notes_for_user_filtered(request.user, **filter_kwargs)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = NoteSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = NoteWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            note = create_note_for_user(request.user, **serializer.validated_data)
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except TagNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'tag_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(NoteSerializer(note).data, status=status.HTTP_201_CREATED)


class NoteDetailView(APIView):
    """
    GET    /api/v1/notes/<id>/ — retrieve a note.
    PATCH  /api/v1/notes/<id>/ — update a note's editable fields.
    DELETE /api/v1/notes/<id>/ — soft-delete a note.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, note_id) -> Response:
        try:
            note = get_note(request.user, note_id)
        except NoteNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'note_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(NoteSerializer(note).data)

    def patch(self, request: Request, note_id) -> Response:
        serializer = NoteWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            note = update_note_for_user(request.user, note_id, **serializer.validated_data)
        except NoteNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'note_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except TagNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'tag_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(NoteSerializer(note).data)

    def delete(self, request: Request, note_id) -> Response:
        try:
            delete_note_for_user(request.user, note_id)
        except NoteNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'note_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class NoteSummaryView(APIView):
    """POST /api/v1/notes/<id>/summary/ — (re)generate the note's AI summary
    through the AI abstraction layer (apps.ai_companion.services)."""

    permission_classes = [IsAuthenticated]
    throttle_scope = 'notes_ai_summary'

    def post(self, request: Request, note_id) -> Response:
        try:
            note = generate_summary_for_user_note(request.user, note_id)
        except NoteNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'note_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except NoteSummaryError as exc:
            return Response(
                {'detail': str(exc), 'code': 'summary_generation_failed'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(NoteSerializer(note).data)


# --------------------------------------------------------------------------
# Attachments
# --------------------------------------------------------------------------


class NoteAttachmentListCreateView(APIView):
    """
    GET  /api/v1/notes/<note_id>/attachments/ — list a note's attachments.
    POST /api/v1/notes/<note_id>/attachments/ — upload an attachment.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request: Request, note_id) -> Response:
        try:
            attachments = list_attachments_for_user_note(request.user, note_id)
        except NoteNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'note_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AttachmentSerializer(attachments, many=True).data)

    def post(self, request: Request, note_id) -> Response:
        uploaded_file = request.FILES.get('file')
        if uploaded_file is None:
            return Response(
                {'detail': 'A file is required.', 'code': 'file_required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            attachment = add_attachment_for_user_note(request.user, note_id, uploaded_file)
        except NoteNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'note_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except AttachmentTooLargeError as exc:
            return Response(
                {'detail': str(exc), 'code': 'attachment_too_large'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AttachmentTypeNotAllowedError as exc:
            return Response(
                {'detail': str(exc), 'code': 'attachment_type_not_allowed'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(AttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)


class NoteAttachmentDetailView(APIView):
    """DELETE /api/v1/notes/<note_id>/attachments/<attachment_id>/ — remove an attachment."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, note_id, attachment_id) -> Response:
        try:
            delete_attachment_for_user_note(request.user, note_id, attachment_id)
        except (NoteNotFoundError, AttachmentNotFoundError) as exc:
            return Response(
                {'detail': str(exc), 'code': 'not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class NoteAttachmentDownloadView(APIView):
    """
    GET /api/v1/notes/<note_id>/attachments/<attachment_id>/download/

    Streams the file only if the requesting user owns the note — this is the
    sole path through which an attachment's bytes are ever served (PROJECT_
    RULES.md Section 8), never a public MEDIA_URL path (see config/settings).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, note_id, attachment_id):
        try:
            attachment = get_attachment_for_user_note(request.user, note_id, attachment_id)
        except (NoteNotFoundError, AttachmentNotFoundError) as exc:
            return Response(
                {'detail': str(exc), 'code': 'not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            attachment.file.open('rb'),
            as_attachment=True,
            filename=attachment.original_filename,
            content_type=attachment.content_type,
        )
