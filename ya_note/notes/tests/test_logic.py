"""Тестируем логику проекта."""

from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNotesLogic(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TITLE = 'Новый текст заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'new-slug-for-second-note'
    MAX_SLUG_LENGTH = 100

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.first_note = Note.objects.create(
            author=cls.author,
            title='Заголовок готовой заметки.',
            text='Текст готовой заметки.',
            slug='test-note-1',
        )

        cls.test_user = User.objects.create(username='Тестовый пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.test_user)

        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': '',
        }
        cls.expected_slug = slugify(cls.NOTE_TITLE)[:cls.MAX_SLUG_LENGTH]

        cls.new_form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.first_note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.first_note.slug,))

    def test_anonymous_user_cant_add_note(self):
        """Проверяем, что анонимный пользователь не может создавать заметки."""
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

    def test_authorized_user_can_add_note(self):
        """Проверяем, что авторизированный клиент может создавать заметки."""
        url = reverse('notes:add')

        self.auth_client.post(url, data=self.form_data)

        self.assertEqual(Note.objects.count(), 2)

        created_note = Note.objects.filter(author=self.test_user.pk).first()

        self.assertEqual(created_note.title, self.NOTE_TITLE)
        self.assertEqual(created_note.text, self.NOTE_TEXT)

        # Проверяем, что слаг заметки формируется автоматически.
        self.assertEqual(created_note.slug, self.expected_slug)

    def test_author_can_edit_note(self):
        """Проверяем, может ли автор изменить свою заметку."""
        self.client.force_login(self.author)
        response = self.client.post(self.edit_url, data=self.new_form_data)
        self.assertRedirects(response, self.success_url)

        self.first_note.refresh_from_db()

        self.assertEqual(self.first_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.first_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.first_note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверяем, что пользователь не может изменить чужую заметку."""
        old_title = self.first_note.title
        old_text = self.first_note.text
        old_slug = self.first_note.slug

        response = self.auth_client.post(
            self.edit_url,
            data=self.new_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.first_note.refresh_from_db()

        self.assertEqual(self.first_note.title, old_title)
        self.assertEqual(self.first_note.text, old_text)
        self.assertEqual(self.first_note.slug, old_slug)

    def test_author_can_delete_note(self):
        """Проверяем, может ли автор удалить свою заметку."""
        self.client.force_login(self.author)
        response = self.client.delete(self.delete_url)

        self.assertRedirects(response, self.success_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_comment_of_another_user(self):
        """Проверяем, что пользователь не сможет удалить чужую заметку."""
        response = self.auth_client.delete(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
