import pytest
from django.urls import reverse
from django.utils import timezone

pytestmark = pytest.mark.django_db


def test_owner_invites_member(family_with_owner, auth_client, other_user):
    response = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    )
    assert response.status_code == 201
    body = response.json()
    assert body['invited_email'] == other_user.email
    assert body['status'] == 'pending'


def test_invite_notifies_registered_invitee(family_with_owner, auth_client, other_user):
    auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    )

    from apps.notifications.repositories import list_notifications_for_user

    notifications = list(list_notifications_for_user(other_user))
    assert len(notifications) == 1
    assert 'invited you' in notifications[0].title


def test_child_cannot_invite(family_with_owner, third_user, third_client, other_user):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_owner, user=third_user, role=FamilyRole.CHILD)

    response = third_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'insufficient_family_permission'


def test_cannot_invite_existing_member(family_with_owner, auth_client, other_user):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_owner, user=other_user, role=FamilyRole.ADULT)

    response = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'already_family_member'


def test_cannot_send_duplicate_pending_invitation(family_with_owner, auth_client, other_user):
    url = reverse('family-invitation-list-create', args=[family_with_owner.id])
    auth_client.post(url, {'email': other_user.email, 'role': 'adult'}, format='json')
    response = auth_client.post(url, {'email': other_user.email, 'role': 'adult'}, format='json')

    assert response.status_code == 409
    assert response.json()['code'] == 'already_family_member'


def test_invite_role_cannot_be_owner(family_with_owner, auth_client, other_user):
    response = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'owner'},
        format='json',
    )
    assert response.status_code == 400


def test_invitee_sees_pending_invitation(family_with_owner, auth_client, other_client, other_user):
    auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    )

    response = other_client.get(reverse('my-invitation-list'))
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]['family']['id'] == str(family_with_owner.id)


def test_accept_invitation_creates_membership(
    family_with_owner, auth_client, other_client, other_user
):
    invite = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    ).json()

    from apps.family.models import FamilyInvitation

    invitation = FamilyInvitation.objects.get(id=invite['id'])

    response = other_client.post(reverse('invitation-accept', args=[invitation.token]))
    assert response.status_code == 200
    assert response.json()['id'] == str(family_with_owner.id)

    members = auth_client.get(
        reverse('family-member-list', args=[family_with_owner.id])
    ).json()
    emails = {m['user']['email'] for m in members}
    assert other_user.email in emails


def test_accept_invitation_wrong_email_rejected(
    family_with_owner, auth_client, third_client, other_user
):
    invite = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    ).json()

    from apps.family.models import FamilyInvitation

    invitation = FamilyInvitation.objects.get(id=invite['id'])

    response = third_client.post(reverse('invitation-accept', args=[invitation.token]))
    assert response.status_code == 403
    assert response.json()['code'] == 'invitation_email_mismatch'


def test_accept_expired_invitation_rejected(
    family_with_owner, auth_client, other_client, other_user
):
    invite = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    ).json()

    from apps.family.models import FamilyInvitation

    invitation = FamilyInvitation.objects.get(id=invite['id'])
    invitation.expires_at = timezone.now() - timezone.timedelta(days=1)
    invitation.save(update_fields=['expires_at'])

    response = other_client.post(reverse('invitation-accept', args=[invitation.token]))
    assert response.status_code == 410
    assert response.json()['code'] == 'invitation_expired'


def test_decline_invitation(family_with_owner, auth_client, other_client, other_user):
    invite = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    ).json()

    from apps.family.models import FamilyInvitation

    invitation = FamilyInvitation.objects.get(id=invite['id'])

    response = other_client.post(reverse('invitation-decline', args=[invitation.token]))
    assert response.status_code == 200
    assert response.json()['status'] == 'declined'


def test_cancel_invitation(family_with_owner, auth_client, other_user):
    invite = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    ).json()

    response = auth_client.delete(
        reverse('family-invitation-cancel', args=[family_with_owner.id, invite['id']])
    )
    assert response.status_code == 204


def test_user_already_in_family_cannot_accept_another_invitation(
    family_with_owner, auth_client, other_client, other_user, third_user, third_client,
):
    from apps.family.models import Family, FamilyRole
    from apps.family.repositories import create_membership

    other_family = Family.objects.create(name='Other Family', created_by=other_user)
    create_membership(family=other_family, user=other_user, role=FamilyRole.OWNER)

    invite = auth_client.post(
        reverse('family-invitation-list-create', args=[family_with_owner.id]),
        {'email': other_user.email, 'role': 'adult'},
        format='json',
    ).json()

    from apps.family.models import FamilyInvitation

    invitation = FamilyInvitation.objects.get(id=invite['id'])

    response = other_client.post(reverse('invitation-accept', args=[invitation.token]))
    assert response.status_code == 409
    assert response.json()['code'] == 'already_in_family'


def test_expire_stale_invitations_service():
    from apps.accounts.models import User
    from apps.family.models import Family, FamilyInvitation, InvitationStatus
    from apps.family.services import expire_stale_invitations

    owner = User.objects.create_user(
        email='owner@example.com', password='CorrectHorse123!', full_name='Owner'
    )
    family = Family.objects.create(name='Stale Family', created_by=owner)
    stale = FamilyInvitation.objects.create(
        family=family,
        invited_email='ghost@example.com',
        role='adult',
        invited_by=owner,
        expires_at=timezone.now() - timezone.timedelta(days=1),
    )
    fresh = FamilyInvitation.objects.create(
        family=family,
        invited_email='fresh@example.com',
        role='adult',
        invited_by=owner,
        expires_at=timezone.now() + timezone.timedelta(days=1),
    )

    count = expire_stale_invitations()

    assert count == 1
    stale.refresh_from_db()
    fresh.refresh_from_db()
    assert stale.status == InvitationStatus.EXPIRED
    assert fresh.status == InvitationStatus.PENDING
