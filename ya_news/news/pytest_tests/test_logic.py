"""Тестируем логику проекта."""
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


def test_authorized_user_can_post_comment(
    author_client,
    author,
    form_data,
    news_detail_url,
    news
):
    """Проверяем, что вошедший пользователь может написать комментарий."""
    response = author_client.post(news_detail_url, form_data)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == 1
    result_comment = Comment.objects.get()
    assert result_comment.text == form_data['text']
    assert result_comment.author == author
    assert result_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news_detail_url, form_data):
    """Проверяем, что анонимный пользователь не может написать комментарий."""
    response = client.post(news_detail_url, form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    author,
    news,
    form_data,
    comment,
    news_detail_url,
    comment_edit_url
):
    """Проверяем, что автор может редактировать свой комментарий."""
    response = author_client.post(comment_edit_url, form_data)
    assertRedirects(response, news_detail_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_other_user_cant_edit_comment(
    reader_client,
    form_data,
    comment,
    comment_edit_url
):
    """Проверяем, что пользователь не иожет редактировать чужой комментарий."""
    response = reader_client.post(comment_edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(
        author_client,
        news_detail_url,
        comment_delete_url
):
    """Проверяем, что автор может удалить свой комментарий."""
    response = author_client.post(comment_delete_url)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(
    reader_client,
    comment_delete_url
):
    """Проверяем, что пользователь не может удалить чужой комментарий."""
    response = reader_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_bad_words_are_banned(
    author_client,
    news_detail_url,
):
    """Тестируем, что комментарий с запрещенными словами не опубликуется."""
    response = author_client.post(
        news_detail_url,
        data={
            'text': f'Текст, {BAD_WORDS[0]}, еще текст {BAD_WORDS[1]}.'
        }
    )
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0
