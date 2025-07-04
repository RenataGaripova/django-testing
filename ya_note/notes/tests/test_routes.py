"""Тестируем маршруты проекта."""
from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='new-note',
        )

        cls.home_url = reverse('notes:home')
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')

    def test_availability_for_list_and_create(self):
        """Тест страниц создания и удаления заметки от лица её автора."""
        urls = (self.add_url, self.list_url, self.success_url)

        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_only_pages_availability(self):
        """Тест страниц заметки, которые доступны только её автору."""
        client_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )

        urls = (self.detail_url, self.edit_url, self.delete_url)

        for client, status in client_statuses:
            for url in urls:
                with self.subTest(user=client, name=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous_client(self):
        """Тест редиректов анонимного пользователя."""
        urls = (
            self.add_url,
            self.list_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )

        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_pages_availability(self):
        """Тест главной страницы, регистрации и входа."""
        urls = (
            self.home_url,
            self.login_url,
            self.signup_url
        )

        for url in urls:
            for user in (self.client, self.author_client):
                with self.subTest(name=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def logout_page_availability(self):
        """Тест страницы выхода из аккаунта."""
        for user in (self.client, self.author_client):
            response = user.post(self.logout_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
