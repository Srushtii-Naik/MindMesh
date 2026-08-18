"""URL routing — Family & Shared Workspace. Namespaced under /api/v1/family/
by the project root config/urls.py."""

from django.urls import path

from apps.family.views import (
    EmergencyContactDetailView,
    EmergencyContactListCreateView,
    FamilyDetailView,
    FamilyInvitationCancelView,
    FamilyInvitationListCreateView,
    FamilyLeaveView,
    FamilyMemberDetailView,
    FamilyMemberListView,
    InvitationAcceptView,
    InvitationDeclineView,
    MyFamilyView,
    MyInvitationListView,
    SharedEventDetailView,
    SharedEventListCreateView,
    SharedNoteDetailView,
    SharedNoteListCreateView,
    SharedTaskCompleteView,
    SharedTaskDetailView,
    SharedTaskEditView,
    SharedTaskListCreateView,
)

urlpatterns = [
    # Static-segment routes registered before <uuid:family_id> captures so
    # they can never be shadowed by them (mirrors apps.notifications.urls).
    path('me/', MyFamilyView.as_view(), name='family-me'),
    path('invitations/', MyInvitationListView.as_view(), name='my-invitation-list'),
    path(
        'invitations/<uuid:token>/accept/',
        InvitationAcceptView.as_view(),
        name='invitation-accept',
    ),
    path(
        'invitations/<uuid:token>/decline/',
        InvitationDeclineView.as_view(),
        name='invitation-decline',
    ),
    path('', MyFamilyView.as_view(), name='family-create'),
    path('<uuid:family_id>/', FamilyDetailView.as_view(), name='family-detail'),
    path('<uuid:family_id>/leave/', FamilyLeaveView.as_view(), name='family-leave'),
    path('<uuid:family_id>/members/', FamilyMemberListView.as_view(), name='family-member-list'),
    path(
        '<uuid:family_id>/members/<uuid:membership_id>/',
        FamilyMemberDetailView.as_view(),
        name='family-member-detail',
    ),
    path(
        '<uuid:family_id>/invitations/',
        FamilyInvitationListCreateView.as_view(),
        name='family-invitation-list-create',
    ),
    path(
        '<uuid:family_id>/invitations/<uuid:invitation_id>/',
        FamilyInvitationCancelView.as_view(),
        name='family-invitation-cancel',
    ),
    path(
        '<uuid:family_id>/emergency-contacts/',
        EmergencyContactListCreateView.as_view(),
        name='emergency-contact-list-create',
    ),
    path(
        '<uuid:family_id>/emergency-contacts/<uuid:contact_id>/',
        EmergencyContactDetailView.as_view(),
        name='emergency-contact-detail',
    ),
    path(
        '<uuid:family_id>/shared-tasks/',
        SharedTaskListCreateView.as_view(),
        name='shared-task-list-create',
    ),
    path(
        '<uuid:family_id>/shared-tasks/<uuid:shared_id>/',
        SharedTaskDetailView.as_view(),
        name='shared-task-detail',
    ),
    path(
        '<uuid:family_id>/shared-tasks/<uuid:shared_id>/task/',
        SharedTaskEditView.as_view(),
        name='shared-task-edit',
    ),
    path(
        '<uuid:family_id>/shared-tasks/<uuid:shared_id>/complete/',
        SharedTaskCompleteView.as_view(),
        name='shared-task-complete',
    ),
    path(
        '<uuid:family_id>/shared-events/',
        SharedEventListCreateView.as_view(),
        name='shared-event-list-create',
    ),
    path(
        '<uuid:family_id>/shared-events/<uuid:shared_id>/',
        SharedEventDetailView.as_view(),
        name='shared-event-detail',
    ),
    path(
        '<uuid:family_id>/shared-notes/',
        SharedNoteListCreateView.as_view(),
        name='shared-note-list-create',
    ),
    path(
        '<uuid:family_id>/shared-notes/<uuid:shared_id>/',
        SharedNoteDetailView.as_view(),
        name='shared-note-detail',
    ),
]
