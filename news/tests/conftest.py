import pytest

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.models import Comment, News


User = get_user_model()


@pytest.fixture
def author():
    return User.objects.create(username='Автор')


@pytest.fixture
def reader():
    return User.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Тестовая новость',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def form_data():
    return {
        'text': 'Новый комментарий',
    }
