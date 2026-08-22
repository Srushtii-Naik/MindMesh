import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _text_file(name='notes.txt', content=b'hello world', content_type='text/plain'):
    return SimpleUploadedFile(name, content, content_type=content_type)


def test_upload_attachment(auth_client, note):
    response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note.id}),
        {'file': _text_file()},
        format='multipart',
    )

    assert response.status_code == 201
    body = response.json()
    assert body['original_filename'] == 'notes.txt'
    assert body['content_type'] == 'text/plain'
    assert body['size_bytes'] == len(b'hello world')


def test_upload_attachment_requires_a_file(auth_client, note):
    response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note.id}), {}, format='multipart'
    )
    assert response.status_code == 400


def test_upload_attachment_rejects_disallowed_content_type(auth_client, note):
    response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note.id}),
        {'file': _text_file(name='virus.exe', content_type='application/x-msdownload')},
        format='multipart',
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'attachment_type_not_allowed'


def test_upload_attachment_rejects_files_over_the_size_limit(auth_client, note, settings):
    settings.NOTE_ATTACHMENT_MAX_SIZE_BYTES = 5

    response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note.id}),
        {'file': _text_file(content=b'this file is definitely over five bytes')},
        format='multipart',
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'attachment_too_large'


def test_upload_attachment_to_other_users_note_returns_404(auth_client, other_user):
    from apps.notes.models import Note

    foreign_note = Note.objects.create(user=other_user, title='Not mine')

    response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': foreign_note.id}),
        {'file': _text_file()},
        format='multipart',
    )
    assert response.status_code == 404


def test_list_attachments(auth_client, note):
    auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note.id}),
        {'file': _text_file()},
        format='multipart',
    )

    response = auth_client.get(reverse('note-attachment-list', kwargs={'note_id': note.id}))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_download_attachment(auth_client, note):
    upload_response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note.id}),
        {'file': _text_file()},
        format='multipart',
    )
    attachment_id = upload_response.json()['id']

    response = auth_client.get(
        reverse(
            'note-attachment-download',
            kwargs={'note_id': note.id, 'attachment_id': attachment_id},
        )
    )

    assert response.status_code == 200
    assert b''.join(response.streaming_content) == b'hello world'


def test_download_other_users_attachment_returns_404(auth_client, other_user):
    from apps.notes.models import Attachment, Note

    foreign_note = Note.objects.create(user=other_user, title='Not mine')
    foreign_attachment = Attachment.objects.create(
        note=foreign_note,
        file=_text_file(),
        original_filename='notes.txt',
        content_type='text/plain',
        size_bytes=11,
    )

    response = auth_client.get(
        reverse(
            'note-attachment-download',
            kwargs={'note_id': foreign_note.id, 'attachment_id': foreign_attachment.id},
        )
    )
    assert response.status_code == 404


def test_delete_attachment(auth_client, note):
    upload_response = auth_client.post(
        reverse('note-attachment-list', kwargs={'note_id': note.id}),
        {'file': _text_file()},
        format='multipart',
    )
    attachment_id = upload_response.json()['id']

    response = auth_client.delete(
        reverse(
            'note-attachment-detail',
            kwargs={'note_id': note.id, 'attachment_id': attachment_id},
        )
    )
    assert response.status_code == 204

    list_response = auth_client.get(reverse('note-attachment-list', kwargs={'note_id': note.id}))
    assert list_response.json() == []
