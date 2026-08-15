"""
End-to-end smoke test — a full user journey through Notes & Knowledge
(ROADMAP.md Milestone 6), chaining every capability in one flow to catch
integration issues that isolated unit/API tests might miss individually.
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_full_notes_journey(auth_client):
    # 1. Create a category and a tag.
    category_response = auth_client.post(
        reverse('note-category-list'), {'name': 'Health'}, format='json'
    )
    assert category_response.status_code == 201
    category_id = category_response.json()['id']

    tag_response = auth_client.post(reverse('note-tag-list'), {'name': 'urgent'}, format='json')
    assert tag_response.status_code == 201
    tag_id = tag_response.json()['id']

    # 2. Create a note using both.
    note_response = auth_client.post(
        reverse('note-list'),
        {
            'title': 'Doctor visit',
            'content': (
                '# Appointment\nBook a follow-up with Dr. Lee. '
                'Bring insurance card. Ask about **test results**.'
            ),
            'category_id': category_id,
            'tag_ids': [tag_id],
        },
        format='json',
    )
    assert note_response.status_code == 201
    note = note_response.json()
    note_id = note['id']
    assert note['category']['id'] == category_id
    assert note['tags'][0]['id'] == tag_id

    # 3. Upload an attachment.
    from django.core.files.uploadedfile import SimpleUploadedFile

    upload_response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note_id}),
        {'file': SimpleUploadedFile('referral.txt', b'referral details', content_type='text/plain')},
        format='multipart',
    )
    assert upload_response.status_code == 201
    attachment_id = upload_response.json()['id']

    # 4. Generate an AI summary.
    summary_response = auth_client.post(reverse('note-summary', kwargs={'note_id': note_id}))
    assert summary_response.status_code == 200
    assert summary_response.json()['ai_summary'] != ''

    # 5. Find it again via category filter, tag filter, and search.
    for params in (
        {'category_id': category_id},
        {'tag_id': tag_id},
        {'search': 'doctor'},
    ):
        list_response = auth_client.get(reverse('note-list'), params)
        assert list_response.status_code == 200
        assert any(item['id'] == note_id for item in list_response.json()['results'])

    # 6. Download the attachment.
    download_response = auth_client.get(
        reverse(
            'note-attachment-download', kwargs={'note_id': note_id, 'attachment_id': attachment_id}
        )
    )
    assert download_response.status_code == 200
    assert b''.join(download_response.streaming_content) == b'referral details'

    # 7. Clean up: delete attachment, then soft-delete the note.
    delete_attachment_response = auth_client.delete(
        reverse(
            'note-attachment-detail', kwargs={'note_id': note_id, 'attachment_id': attachment_id}
        )
    )
    assert delete_attachment_response.status_code == 204

    delete_note_response = auth_client.delete(reverse('note-detail', kwargs={'note_id': note_id}))
    assert delete_note_response.status_code == 204

    final_get = auth_client.get(reverse('note-detail', kwargs={'note_id': note_id}))
    assert final_get.status_code == 404
