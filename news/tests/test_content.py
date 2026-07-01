from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment, News

pytestmark = pytest.mark.django_db


@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    comments = []

    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)

    return comments


def test_news_count(client, news_list):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']

    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']

    dates = [news.date for news in object_list]

    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, news, comments):
    response = client.get(reverse('news:detail', args=(news.pk,)))

    news_object = response.context['news']
    all_comments = news_object.comment_set.all()

    created_dates = [
        comment.created for comment in all_comments
    ]

    assert created_dates == sorted(created_dates)


def test_anonymous_user_has_no_form(client, detail_url):
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authorized_user_has_form(author_client, detail_url):
    response = author_client.get(detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
