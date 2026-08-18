import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_create_family_requires_authentication(api_client):
    response = api_client.post(reverse('family-create'), {'name': 'The Does'}, format='json')
    assert response.status_code == 401


def test_create_family_makes_requester_owner(auth_client, user):
    response = auth_client.post(reverse('family-create'), {'name': 'The Does'}, format='json')

    assert response.status_code == 201
    assert response.json()['name'] == 'The Does'

    members = auth_client.get(
        reverse('family-member-list', args=[response.json()['id']])
    ).json()
    assert len(members) == 1
    assert members[0]['role'] == 'owner'
    assert members[0]['user']['email'] == user.email


def test_create_family_blank_name_rejected(auth_client):
    response = auth_client.post(reverse('family-create'), {'name': '   '}, format='json')
    assert response.status_code == 400


def test_user_cannot_create_second_family(auth_client, family_with_owner):
    response = auth_client.post(reverse('family-create'), {'name': 'Another Family'}, format='json')
    assert response.status_code == 409
    assert response.json()['code'] == 'already_in_family'


def test_get_my_family_returns_404_when_none(auth_client):
    response = auth_client.get(reverse('family-me'))
    assert response.status_code == 404
    assert response.json()['code'] == 'family_not_found'


def test_get_my_family(auth_client, family_with_owner):
    response = auth_client.get(reverse('family-me'))
    assert response.status_code == 200
    assert response.json()['id'] == str(family_with_owner.id)


def test_rename_family_as_owner(auth_client, family_with_owner):
    response = auth_client.patch(
        reverse('family-detail', args=[family_with_owner.id]), {'name': 'The Roes'}, format='json'
    )
    assert response.status_code == 200
    assert response.json()['name'] == 'The Roes'


def test_rename_family_requires_membership(other_client, family_with_owner):
    response = other_client.patch(
        reverse('family-detail', args=[family_with_owner.id]), {'name': 'Hijacked'}, format='json'
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'not_family_member'


def test_child_member_cannot_rename_family(family_with_owner, third_client, third_user):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_owner, user=third_user, role=FamilyRole.CHILD)

    response = third_client.patch(
        reverse('family-detail', args=[family_with_owner.id]), {'name': 'Nope'}, format='json'
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'insufficient_family_permission'


def test_owner_promotes_member_and_leaves(
    family_with_owner, user, other_user, other_client, auth_client
):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership, get_membership_for_user_family

    create_membership(family=family_with_owner, user=other_user, role=FamilyRole.ADULT)
    membership = get_membership_for_user_family(other_user, family_with_owner.id)

    promote = auth_client.patch(
        reverse('family-member-detail', args=[family_with_owner.id, membership.id]),
        {'role': 'owner'},
        format='json',
    )
    assert promote.status_code == 200
    assert promote.json()['role'] == 'owner'

    leave = auth_client.post(reverse('family-leave', args=[family_with_owner.id]))
    assert leave.status_code == 204

    members = other_client.get(reverse('family-member-list', args=[family_with_owner.id])).json()
    assert len(members) == 1
    assert members[0]['role'] == 'owner'


def test_sole_owner_cannot_leave_while_others_remain(family_with_owner, other_user, auth_client):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_owner, user=other_user, role=FamilyRole.ADULT)

    response = auth_client.post(reverse('family-leave', args=[family_with_owner.id]))
    assert response.status_code == 409
    assert response.json()['code'] == 'cannot_remove_last_owner'


def test_sole_owner_and_sole_member_can_leave(family_with_owner, auth_client):
    response = auth_client.post(reverse('family-leave', args=[family_with_owner.id]))
    assert response.status_code == 204

    check = auth_client.get(reverse('family-me'))
    assert check.status_code == 404


def test_owner_removes_member(family_with_owner, other_user, auth_client, other_client):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership, get_membership_for_user_family

    create_membership(family=family_with_owner, user=other_user, role=FamilyRole.ADULT)
    membership = get_membership_for_user_family(other_user, family_with_owner.id)

    response = auth_client.delete(
        reverse('family-member-detail', args=[family_with_owner.id, membership.id])
    )
    assert response.status_code == 204

    check = other_client.get(reverse('family-me'))
    assert check.status_code == 404


def test_non_owner_cannot_remove_member(family_with_owner, other_user, third_user, third_client):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership, get_membership_for_user_family

    create_membership(family=family_with_owner, user=other_user, role=FamilyRole.ADULT)
    create_membership(family=family_with_owner, user=third_user, role=FamilyRole.ADULT)
    target = get_membership_for_user_family(other_user, family_with_owner.id)

    response = third_client.delete(
        reverse('family-member-detail', args=[family_with_owner.id, target.id])
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'insufficient_family_permission'


def test_cannot_remove_last_owner(family_with_owner, user, auth_client):
    from apps.family.repositories import get_membership_for_user_family

    membership = get_membership_for_user_family(user, family_with_owner.id)

    response = auth_client.delete(
        reverse('family-member-detail', args=[family_with_owner.id, membership.id])
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'cannot_remove_last_owner'


def test_data_isolation_family_scoped_by_membership(family_with_owner, other_client):
    """A user who is not a member of a family can't read its members —
    ROADMAP.md Milestone 10 checklist: "Data isolation verified"."""
    response = other_client.get(reverse('family-member-list', args=[family_with_owner.id]))
    assert response.status_code == 403
