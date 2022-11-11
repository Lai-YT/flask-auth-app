from __future__ import annotations
from http import HTTPStatus
from typing import TYPE_CHECKING, no_type_check

import pytest
from flask import session
from flask_login import current_user, login_remembered
from sqlalchemy import Select

from auth_app.db import db
from auth_app.models import User
from tests.util import captured_flash_messages, captured_templates

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient
    from werkzeug.test import TestResponse


class TestRegister:
    @pytest.fixture
    def user_data(self) -> User:
        return User(email='123@email.com', name='123', password='123pwd')

    @staticmethod
    def test_should_render_register_html(app: Flask) -> None:
        with captured_templates(app) as templates:

            response: TestResponse = app.test_client().get('/register')

            assert response.status_code == HTTPStatus.OK
            assert len(templates) == 1
            template, = templates
            assert template.name == 'register.html'

    @staticmethod
    def test_should_add_record_to_database(client: FlaskClient, user_data: User) -> None:
        with client:

            client.post('/register', data=user_data.__dict__)

            stmt: Select = db.select(User).where(User.email == user_data.email)
            user: User = db.session.execute(stmt).scalars().first()
            assert user.email == user_data.email
            assert user.name == user_data.name

    @staticmethod
    def test_should_redirect_to_login_if_succeeded(client: FlaskClient, user_data: User) -> None:
        response: TestResponse = client.post('/register', data=user_data.__dict__)

        assert response.location == '/login'

    @staticmethod
    def test_should_stay_in_register_if_email_already_registered(
            client: FlaskClient, user_data: User) -> None:
        client.post('/register', data=user_data.__dict__)

        response: TestResponse = client.post('/register', data=user_data.__dict__)

        assert response.location == '/register'

    @staticmethod
    def test_should_flash_message_if_email_already_registered(app: Flask) -> None:
        with captured_flash_messages(app) as messages:

            response: TestResponse = app.test_client().post(
                '/register',
                data={
                    'name': 'someone',
                    'email': 'other@email.com',
                    'password': 'someonepwd'})

            assert response.status_code == HTTPStatus.FOUND
            assert len(messages) == 1
            message, = messages
            assert message == 'Email address already registered.'


class TestLogin:
    @staticmethod
    def test_should_redirect_to_profile_if_succeeded(client: FlaskClient) -> None:
        response: TestResponse = client.post(
            '/login',
            data={
                'email': 'test@email.com',
                'password': 'test'})

        assert response.location == '/profile'

    @staticmethod
    def test_should_render_login_html(app: Flask) -> None:
        with captured_templates(app) as templates:

            response: TestResponse = app.test_client().get('/login')

            assert response.status_code == HTTPStatus.OK
            assert len(templates) == 1
            template, = templates
            assert template.name == 'login.html'

    @staticmethod
    def test_should_stay_in_login_if_failed(client: FlaskClient) -> None:
        response: TestResponse = client.post(
            '/login',
            data={
                'email': 'someone@email.com',
                'password': 'someone'})

        assert response.location == '/login'

    @staticmethod
    def test_should_flash_message_if_wrong_password(app: Flask) -> None:
        with captured_flash_messages(app) as messages:

            response: TestResponse = app.test_client().post(
                '/login',
                data={
                    'email': 'test@email.com',
                    'password': 'should_be_test'})

            assert response.status_code == HTTPStatus.FOUND
            assert len(messages) == 1
            message, = messages
            assert message == 'Please check your login details and try again.'

    @staticmethod
    def test_should_flash_message_if_unregistered_user(app: Flask) -> None:
        with captured_flash_messages(app) as messages:

            response: TestResponse = app.test_client().post(
                '/login',
                data={
                    'email': 'someone@email.com',
                    'password': 'someone'})

            assert response.status_code == HTTPStatus.FOUND
            assert len(messages) == 1
            message, = messages
            assert message == 'Please check your login details and try again.'

    @staticmethod
    def test_should_add_user_id_into_session(client: FlaskClient) -> None:
        with client:

            client.post(
                '/login',
                data={
                    'email': 'test@email.com',
                    'password': 'test'})

            stmt: Select = db.select(User.id).where(User.email == 'test@email.com')
            user_id: int = db.session.execute(stmt).scalars().first()
            assert session['_user_id'] == str(user_id)

    def test_should_keep_user_authenticated_if_remember(
            self, app: Flask, client: FlaskClient) -> None:
        @app.route('/username')
        def username():
            if current_user.is_authenticated:
                return current_user.name
            return "anonymous"

        client.post(
            '/login',
            data={
                'email': 'test@email.com',
                'password': 'test',
                'remember': 'any-value'})
        with client.session_transaction() as session:
            session.clear()

        response: TestResponse = client.get('/username')
        assert response.data == b'test'


class TestLogout:
    @staticmethod
    def test_should_be_login_required(client: FlaskClient) -> None:
        response: TestResponse = client.get('/logout')

        assert response.status_code == HTTPStatus.FOUND
        assert response.location == r'/login?next=%2Flogout'

    @staticmethod
    def test_should_clear_session(client: FlaskClient) -> None:
        with client:
            client.post('/login', data={'email': 'test@email.com', 'password': 'test'})

            client.get('/logout')

            assert '_user_id' not in session

    @staticmethod
    def test_should_render_index_html(app: Flask) -> None:
        with captured_templates(app) as templates:
            # login required
            client: FlaskClient = app.test_client()
            client.post('/login', data={'email': 'test@email.com', 'password': 'test'})

            response: TestResponse = client.get('/logout')

            assert response.status_code == HTTPStatus.OK
            assert len(templates) == 1
            template, = templates
            assert template.name == 'index.html'
