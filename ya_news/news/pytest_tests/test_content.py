"""Тестируем контент на страницах проекта."""
import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.usefixtures('create_news_list')
def test_news_count(client, home_url):
    """Проверяем, что на главную страницу выводятся максимум 10 новостей."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('create_news_list')
def test_news_order(client, home_url):
    """Проверяем порядок новостей на главной странице."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    dates_list = [news.date for news in object_list]
    sorted_dates = sorted(dates_list, reverse=True)
    assert dates_list == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('create_comment_list')
def test_comments_order(client, news_detail_url):
    """Проверяем порядок комментариев к новости."""
    response = client.get(news_detail_url)
    assert 'news' in response.context
    response_news = response.context['news']
    comment_list = response_news.comment_set.all()
    timestamps = [comment.created for comment in comment_list]
    sorted_timestamps = sorted(timestamps)
    assert timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_detail_url):
    """Проверяем отсутствие формы для комментария у анонимного клиента."""
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_detail_url):
    """Проверяем наличие формы для комментария у авторизированного клиента."""
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
