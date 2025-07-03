"""Тестируем контент на страницах проекта."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesContent(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        cls.note = Note.objects.create(
            author=cls.author,
            title='Заметка автора',
            text='Текст к заметке.',
            slug='new-note',
        )

    def test_notes_context(self):
        """Проверка словаря context."""
        response = self.auth_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_single_user_notes(self):
        """Проверяем, что пользователь видит только свои записи."""
        self.client.force_login(self.not_author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_add_and_edit_forms(self):
        """Проверка форм на страницах создания и редактирования заметки."""
        urls = (
            ('notes:add', None),
            ('notes:edit', ('new-note',)),
        )

        for url_name, args in urls:
            with self.subTest(name=url_name):
                url = reverse(url_name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
