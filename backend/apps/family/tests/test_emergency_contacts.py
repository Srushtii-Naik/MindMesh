import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _contacts_url(family_id):
    return reverse('emergency-contact-list-create', args=[family_id])


def test_owner_creates_emergency_contact(family_with_owner, auth_client):
    response = auth_client.post(
        _contacts_url(family_with_owner.id),
        {'name': 'Dr. Smith', 'relationship': 'Family doctor', 'phone_number': '555-0100'},
        format='json',
    )
    assert response.status_code == 201
    assert response.json()['name'] == 'Dr. Smith'


def test_blank_name_rejected(family_with_owner, auth_client):
    response = auth_client.post(
        _contacts_url(family_with_owner.id),
        {'name': '  ', 'phone_number': '555-0100'},
        format='json',
    )
    assert response.status_code == 400


def test_child_cannot_create_emergency_contact(family_with_owner, third_user, third_client):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_owner, user=third_user, role=FamilyRole.CHILD)

    response = third_client.post(
        _contacts_url(family_with_owner.id),
        {'name': 'Dr. Smith', 'phone_number': '555-0100'},
        format='json',
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'insufficient_family_permission'


def test_child_can_view_emergency_contacts(
    family_with_owner, auth_client, third_user, third_client
):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_owner, user=third_user, role=FamilyRole.CHILD)
    auth_client.post(
        _contacts_url(family_with_owner.id),
        {'name': 'Dr. Smith', 'phone_number': '555-0100'},
        format='json',
    )

    response = third_client.get(_contacts_url(family_with_owner.id))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_non_member_cannot_view_emergency_contacts(family_with_owner, other_client):
    response = other_client.get(_contacts_url(family_with_owner.id))
    assert response.status_code == 403
    assert response.json()['code'] == 'not_family_member'


def test_update_emergency_contact(family_with_owner, auth_client):
    created = auth_client.post(
        _contacts_url(family_with_owner.id),
        {'name': 'Dr. Smith', 'phone_number': '555-0100'},
        format='json',
    ).json()

    response = auth_client.patch(
        reverse('emergency-contact-detail', args=[family_with_owner.id, created['id']]),
        {'phone_number': '555-0199'},
        format='json',
    )
    assert response.status_code == 200
    assert response.json()['phone_number'] == '555-0199'


def test_delete_emergency_contact_is_soft_delete(family_with_owner, auth_client):
    created = auth_client.post(
        _contacts_url(family_with_owner.id),
        {'name': 'Dr. Smith', 'phone_number': '555-0100'},
        format='json',
    ).json()

    response = auth_client.delete(
        reverse('emergency-contact-detail', args=[family_with_owner.id, created['id']])
    )
    assert response.status_code == 204

    from apps.family.models import EmergencyContact

    contact = EmergencyContact.objects.get(id=created['id'])
    assert contact.is_active is False
    assert contact.deleted_at is not None

    listing = auth_client.get(_contacts_url(family_with_owner.id))
    assert listing.json() == []
