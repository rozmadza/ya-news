from http import HTTPStatus

import pytest

from django.urls import reverse

from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous(client, name, args):
    if name == 'news:detail':
        url = reverse(name, args=(args.pk,))
    else:
        url = reverse(name)

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability_for_anonymous(client):
    url = reverse('users:logout')
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'url_fixture',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ),
)
def test_comment_pages_availability(
    client_fixture,
    expected_status,
    url_fixture,
):
    response = client_fixture.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ),
)
def test_redirect_for_anonymous_client(
    client,
    url_fixture,
):
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url_fixture}'

    response = client.get(url_fixture)

    assertRedirects(response, expected_url)
