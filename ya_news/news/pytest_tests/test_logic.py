"""Тестируем логику проекта."""

from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


def test_authorized_user_can_post_comment(
    author_client,
    author,
    form_data,
    news_detail_url
):
    """Проверяем, что вошедший пользователь может написать комментарий."""
    response = author_client.post(news_detail_url, form_data)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == 1
    result_comment = Comment.objects.get()
    assert result_comment.text == form_data['text']
    assert result_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news_detail_url, form_data):
    """Проверяем, что анонимный пользователь не может написать комментарий."""
    response = client.post(news_detail_url, form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


# В параметрах вызвана фикстура note: значит, в БД создана заметка.
def test_author_can_edit_comment(
    author_client,
    form_data,
    comment,
    news_detail_url
):
    """Проверяем, что автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, news_detail_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(
    reader_client,
    form_data,
    comment,
    news_detail_url
):
    """Проверяем, что автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, comment, news_detail_url):
    """Проверяем, что автор может редактировать свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(
    reader_client,
    comment,
    news_detail_url
):
    """Проверяем, что автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_bad_words_are_banned(
    author_client,
    news_detail_url,
    bad_words_example
):
    """Тестируем, что комментарий с запрещенными словами не опубликуется."""
    response = author_client.post(news_detail_url, data=bad_words_example)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0
