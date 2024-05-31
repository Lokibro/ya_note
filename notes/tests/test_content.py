from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.guest = User.objects.create(
            username='Гость'
        )
        cls.note = Note.objects.create(
                title=f'Заголовок',
                text='Текст заметки',
                slug=f'slug_note',
                author=cls.author
        )
        cls.list_url = reverse('notes:list')

    def test_notes_list_for_different_users(self):
        users_status =(
            (self.author, True),
            (self.guest, False)
        )
        for user, status in users_status:
            with self.subTest(user):
                self.client.force_login(user)
                response = self.client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertEquals(
                    (self.note in object_list), status
                )


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', kwargs={'slug': cls.note.slug})
        cls.edit_url = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.add_url = reverse('notes:add')

    def test_authorized_client_has_select_content(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('note', response.context)

    def test_authorized_client_has_add_edit_form(self):
        self.client.force_login(self.author)
        for url in (self.add_url, self.edit_url):
            with self.subTest(url):
                response = self.client.get(self.edit_url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
