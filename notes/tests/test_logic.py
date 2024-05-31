from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestCreationNote(TestCase):

    NEW_TEXT = 'Это новый текс'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.url_done = reverse('notes:success')
        cls.url_add = reverse('notes:add')
        cls.url_delete = reverse('notes:delete', kwargs={'slug': cls.note.slug})
        cls.url_edit = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': cls.NEW_TEXT
        }

    def test_author_can_add_note_and_redirect_to_success(self):
        count_notes = Note.objects.count()
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.url_done)
        self.assertEquals(Note.objects.count(), count_notes + 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        self.note.refresh_from_db()
        self.assertEquals(self.note.text, self.NEW_TEXT)

    def test_emply_slug_convert_from_title(self):
        new_form_data = {
            'title': 'Привет',
            'text': 'Просто текст'
        }
        self.author_client.post(self.url_add, data=new_form_data)
        note = Note.objects.get(slug=slugify(new_form_data['title']))
        self.assertIsNotNone(note)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_done)
        notes_count = Note.objects.count()
        self.assertEquals(notes_count, 0)

