from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoute(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='slug_note',
            author=cls.author
        )
        cls.guest = User.objects.create(
            username='Гость'
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_delete(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.guest, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name, kwargs in urls:
                with self.subTest(name=name):
                    url = reverse(name, kwargs=kwargs)
                    response = self.client.get(url)
                    self.assertEquals(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
            ('notes:list', None),
        )
        for name, kwargs in urls:
            with self.subTest(naem=name):
                url = reverse(name, kwargs=kwargs)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
