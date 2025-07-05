"""Тестируем маршруты проекта."""
from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        lazy_fixture('news_detail_url'),
        lazy_fixture('home_url'),
        lazy_fixture('login_url'),
        lazy_fixture('signup_url')
    ),
)
def test_pages_availability_for_anonymous_user(client, url):
    """Тестируем страницы, которые доступны анонимному пользователю."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_page_availability(client, logout_url):
    """Тест на доступ к странице выхода."""
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        lazy_fixture('comment_edit_url'),
        lazy_fixture('comment_delete_url'),
    )
)
def test_comment_edit_and_delete_for_author(
    parametrized_client,
    expected_status,
    url,
):
    """Тестируем доступ к страницам удаления и редактирования комментария."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        lazy_fixture('comment_edit_url'),
        lazy_fixture('comment_delete_url'),
    )
)
def test_anonymous_user_redirects(client, url):
    """Тест на редирект анонимного пользователя с недоступных ему страниц."""
    login_url = reverse('users:login')
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
