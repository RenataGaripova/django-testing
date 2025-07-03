"""Тестируем маршруты проекта."""

import pytest

from pytest_lazyfixture import lazy_fixture

from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:detail', lazy_fixture('news')),
        ('news:home', None),
        ('users:login', None),
        ('users:signup', None),
        ('users:logout', None),
    ),
)
def test_homepage_availability_for_anonymous_user(client, name, news_object):
    """Тестируем страницы, которые доступны анонимному пользователю."""
    if news_object is not None:
        url = reverse(name, args=(news_object.id,))
    else:
        url = reverse(name)

    if name != 'users:logout':
        response = client.get(url)
    else:
        response = client.post(url)

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
    'name',
    ('news:edit', 'news:delete')
)
def test_comment_edit_and_delete_for_author(
    parametrized_client,
    expected_status,
    name,
    comment
):
    """Тестируем доступ к страницам удаления и редактирования комментария."""
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_anonymous_user_redirects(client, name, comment):
    """Тест на редирект анонимного пользователя с недоступных ему страниц."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
