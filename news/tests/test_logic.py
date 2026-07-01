from http import HTTPStatus

import pytest

from django.urls import reverse

from pytest_django.asserts import (
    assertFormError,
    assertRedirects,
)

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
    client,
    detail_url,
    form_data,
):
    client.post(detail_url, data=form_data)

    assert Comment.objects.count() == 0


def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url,
    form_data,
):
    response = author_client.post(
        detail_url,
        data=form_data,
    )

    assertRedirects(response, f'{detail_url}#comments')

    assert Comment.objects.count() == 1

    comment = Comment.objects.get()

    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(
    author_client,
    detail_url,
):
    bad_words_data = {
        'text': f'Текст, {BAD_WORDS[0]}, текст',
    }

    response = author_client.post(
        detail_url,
        data=bad_words_data,
    )

    assertFormError(
        response.context['form'],
        'text',
        WARNING,
    )

    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_url,
):
    new_data = {
        'text': 'Обновленный комментарий',
    }

    response = author_client.post(
        edit_url,
        data=new_data,
    )

    expected_url = (
        reverse('news:detail', args=(comment.news.pk,))
        + '#comments'
    )

    assertRedirects(response, expected_url)

    comment.refresh_from_db()

    assert comment.text == new_data['text']


def test_author_can_delete_comment(
    author_client,
    comment,
    delete_url,
):
    response = author_client.delete(delete_url)

    expected_url = (
        reverse('news:detail', args=(comment.news.pk,))
        + '#comments'
    )

    assertRedirects(response, expected_url)

    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'url_fixture',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ),
)
def test_reader_cant_edit_or_delete_comment(
    reader_client,
    comment,
    url_fixture,
    form_data,
):
    if 'edit' in url_fixture:
        response = reader_client.post(
            url_fixture,
            data=form_data,
        )
    else:
        response = reader_client.delete(url_fixture)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()

    assert comment.text == 'Текст комментария'
    assert Comment.objects.count() == 1
