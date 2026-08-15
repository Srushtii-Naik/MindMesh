import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_generate_summary(auth_client, note):
    note.content = 'First sentence about the meeting. Second sentence with details. Third sentence.'
    note.save()

    response = auth_client.post(reverse('note-summary', kwargs={'note_id': note.id}))

    assert response.status_code == 200
    body = response.json()
    assert body['ai_summary'] != ''
    assert body['ai_summary_generated_at'] is not None


def test_generate_summary_for_empty_note_fails_gracefully(auth_client, user):
    from apps.notes.models import Note

    empty_note = Note.objects.create(user=user, title='Empty', content='')

    response = auth_client.post(reverse('note-summary', kwargs={'note_id': empty_note.id}))

    assert response.status_code == 502
    assert response.json()['code'] == 'summary_generation_failed'


def test_generate_summary_for_other_users_note_returns_404(auth_client, other_user):
    from apps.notes.models import Note

    foreign_note = Note.objects.create(user=other_user, title='Not mine', content='Some content.')

    response = auth_client.post(reverse('note-summary', kwargs={'note_id': foreign_note.id}))
    assert response.status_code == 404


def test_summary_is_persisted_and_returned_on_subsequent_reads(auth_client, note):
    note.content = 'Some content to summarize here.'
    note.save()

    auth_client.post(reverse('note-summary', kwargs={'note_id': note.id}))

    detail_response = auth_client.get(reverse('note-detail', kwargs={'note_id': note.id}))
    assert detail_response.json()['ai_summary'] != ''
