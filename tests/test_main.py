from __future__ import annotations
from http import HTTPStatus
from typing import TYPE_CHECKING

from tests.util import captured_templates

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient
    from werkzeug.test import TestResponse


def test_index_should_render_index_html(app: Flask) -> None:
    with captured_templates(app) as templates:

        response: TestResponse = app.test_client().get('/')

        assert response.status_code == HTTPStatus.OK
        assert len(templates) == 1
        template, = templates
        assert template.name == 'index.html'


def test_profile_should_be_login_required(client: FlaskClient) -> None:
    response: TestResponse = client.get('/profile')

    assert response.status_code == HTTPStatus.FOUND
    assert response.location == r'/login?next=%2Fprofile'


def test_profile_should_render_profile_html(app: Flask) -> None:
    with captured_templates(app) as templates:
        client: FlaskClient = app.test_client()
        # login required
        client.post('login', data={'email': 'test@email.com', 'password': 'test'})

        response: TestResponse = client.get('/profile')

        assert response.status_code == HTTPStatus.OK
        assert len(templates) == 1
        template, = templates
        assert template.name == 'profile.html'
