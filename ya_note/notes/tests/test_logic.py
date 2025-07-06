"""Тестируем логику проекта."""
from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNotesLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.test_user = User.objects.create(username='Новый пользователь')
        cls.test_client = Client()
        cls.test_client.force_login(cls.test_user)

        cls.first_note = Note.objects.create(
            author=cls.author,
            title='Заголовок готовой заметки.',
            text='Текст готовой заметки.',
            slug='test-note-1',
        )

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'test-note-slug',
        }

        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.first_note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.first_note.slug,))

    def test_anonymous_user_cant_add_note(self):
        """Проверяем, что анонимный пользователь не может создавать заметки."""
        initial_note_count = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), initial_note_count)

    def test_authorized_user_can_add_note(self):
        """Проверяем, что авторизированный клиент может создавать заметки."""
        Note.objects.all().delete()

        self.test_client.post(self.add_url, data=self.form_data)

        self.assertEqual(Note.objects.count(), 1)

        created_note = Note.objects.get()

        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.slug, self.form_data['slug'])
        self.assertEqual(created_note.author, self.test_user)

    def test_auto_slug_creation(self):
        """Проверяем, что для пустого поля слаг формируется автоматически."""
        Note.objects.all().delete()

        self.form_data.pop('slug')

        response = self.test_client.post(self.add_url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)

        created_note = Note.objects.get()

        assert created_note.slug == slugify(self.form_data['title'])

    def test_author_can_edit_note(self):
        """Проверяем, может ли автор изменить свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        self.first_note.refresh_from_db()

        self.assertEqual(self.first_note.title, self.form_data['title'])
        self.assertEqual(self.first_note.text, self.form_data['text'])
        self.assertEqual(self.first_note.slug, self.form_data['slug'])
        self.assertEqual(self.first_note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверяем, что пользователь не может изменить чужую заметку."""
        response = self.test_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        current_note = Note.objects.get(pk=self.first_note.id)

        self.assertEqual(self.first_note.title, current_note.title)
        self.assertEqual(self.first_note.text, current_note.text)
        self.assertEqual(self.first_note.slug, current_note.slug)
        self.assertEqual(self.first_note.author, current_note.author)

    def test_author_can_delete_note(self):
        """Проверяем, может ли автор удалить свою заметку."""
        initial_note_count = Note.objects.count()

        response = self.author_client.delete(self.delete_url)

        self.assertRedirects(response, self.success_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_note_count - 1)

    def test_user_cant_delete_comment_of_another_user(self):
        """Проверяем, что пользователь не сможет удалить чужую заметку."""
        initial_note_count = Note.objects.count()

        response = self.test_client.delete(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_note_count)

    def test_not_unique_slug(self):
        """Проверяем, что нельзя создать две заметки с одинаковым слагом."""
        initial_note_count = Note.objects.count()

        self.form_data['slug'] = self.first_note.slug
        response = self.test_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response.context['form'],
            'slug',
            errors=(self.first_note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), initial_note_count)
