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
        cls.reader = User.objects.create(username='Читатель простой')

        cls.test_auth_client = User.objects.create(
            username='Авторизированный пользователь'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.test_auth_client)

        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='new-note',
        )

    def test_availability_for_list_and_create(self):
        """Тест страниц создания и удаления заметки от лица её автора."""
        urls = ('notes:add', 'notes:list', 'notes:success',)

        for url_name in urls:
            with self.subTest(name=url_name):
                url = reverse(url_name)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_only_pages_availability(self):
        """Тест страниц заметки, которые доступны только её автору."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        urls = ('notes:detail', 'notes:edit', 'notes:delete',)

        for user, status in users_statuses:
            self.client.force_login(user)
            for url_name in urls:
                with self.subTest(user=user, name=url_name):
                    url = reverse(url_name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous_client(self):
        """Тест редиректов анонимного пользователя."""
        login_url = reverse('users:login')

        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        for url_name, args in urls:
            with self.subTest(name=url_name):
                url = reverse(url_name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_pages_availability(self):
        """Тест главной страницы, регистрации, входа и выхода."""
        urls = (
            ('notes:home', 'get'),
            ('users:login', 'get'),
            ('users:signup', 'get'),
            ('users:logout', 'post'),
        )

        for url_name, method in urls:
            for user in (self.client, self.auth_client):
                with self.subTest(name=url_name):
                    url = reverse(url_name)
                    if method == 'get':
                        response = user.get(url)
                    else:
                        response = user.post(url)

                    self.assertEqual(response.status_code, HTTPStatus.OK)
