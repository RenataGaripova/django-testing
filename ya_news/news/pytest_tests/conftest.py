"""Фикстуры к тестам."""
from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура пользователя - автора комментариев."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Фикстура пользователя - читателя комментариев."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Фикстура, возвращающая залогиненного автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Фикстура, возвращающая залогиненного читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Фикстура новости."""
    return News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    """Фикстура комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def create_news_list():
    """Фикстура списка новостей."""
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def create_comment_list(news, author):
    """Фикстура списка комментариев."""
    Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text='Текст комментария',
            created=timezone.now() + timedelta(days=index),
        )
        for index in range(5)
    )


@pytest.fixture
def home_url():
    """Фикстура для получения url главной страницы."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Фикстура для получения url главной страницы."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Фикстура для получения url главной страницы."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Фикстура для получения url главной страницы."""
    return reverse('users:signup')


@pytest.fixture
def news_detail_url(news):
    """Фикстура для получения url страницы одной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_edit_url(comment):
    """Фикстура для получения url страницы редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    """Фикстура для получения url страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def form_data():
    """Фикстура с данными для отправки комментария."""
    return {
        'text': 'Текст нового комментария.',
    }
