"""Тестируем контент на страницах проекта."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            author=cls.author,
            title='Заметка автора',
            text='Текст к заметке.',
            slug='new-note',
        )

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_context(self):
        """Проверка словаря context."""
        client_and_expected_result = (
            (self.author_client, True),
            (self.not_author_client, False)
        )

        for client, result in client_and_expected_result:
            with self.subTest(name=self.list_url):
                response = client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), result)

    def test_add_and_edit_forms(self):
        """Проверка форм на страницах создания и редактирования заметки."""
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest():
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
