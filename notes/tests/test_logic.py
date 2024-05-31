from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestCreationNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.url_done = reverse('notes:success')
        cls.url_add = reverse('notes:add')
        cls.url_login = reverse('users:login')
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Это новый текс',
            'slug': 'slug-slug'
        }

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, self.url_done)
        self.assertEquals(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEquals(new_note.title, self.form_data['title'])
        self.assertEquals(new_note.text, self.form_data['text'])
        self.assertEquals(new_note.slug, self.form_data['slug'])
        self.assertEquals(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        client = Client()
        response = client.post(self.url_add, data=self.form_data)
        expected_url = f'{self.url_login}?next={self.url_add}'
        self.assertRedirects(response, expected_url)
        self.assertEquals(Note.objects.count(), 0)


class TestSlugNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note(
            title='Заголовок',
            text='Текст',
            slug='slug-slug',
            author=cls.author
        )
        cls.url_done = reverse('notes:success')
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse(
            'notes:edit',
            kwargs={'slug': cls.note.slug}
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Это новый текс',
            'slug': 'slug-slug'
        }

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug-slug',
            author=self.author
        )
        response = self.author_client.post(self.url_add, self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
        self.assertEquals(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.url_add, self.form_data)
        self.assertRedirects(response, self.url_done)
        self.assertEquals(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEquals(new_note.slug, expected_slug)


class TestEditDeleteNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug-slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Это новый текс',
            'slug': 'slugy'
        }
        cls.url_edit = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.url_delete = reverse('notes:delete', kwargs={'slug': cls.note.slug})
        cls.url_done = reverse('notes:success')

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, self.form_data)
        self.assertRedirects(response, self.url_done)
        self.note.refresh_from_db()
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEquals(note_from_db.title, self.note.title)
        self.assertEquals(note_from_db.text, self.note.text)
        self.assertEquals(note_from_db.slug, self.note.slug)

    def test_other_user_cant_edie_note(self):
        response = self.not_author_client.post(self.url_edit, self.form_data)
        self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEquals(self.note.title, note_from_db.title)
        self.assertEquals(self.note.text, note_from_db.text)
        self.assertEquals(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.url_delete, kwargs={'slug': self.note.slug})
        self.assertRedirects(response, self.url_done)
        self.assertEquals(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.not_author_client.post(self.url_delete, kwargs={'slug': self.note.slug})
        self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEquals(Note.objects.count(), 1)
