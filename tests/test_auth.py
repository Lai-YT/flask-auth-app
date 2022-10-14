from __future__ import annotations
import sqlite3
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

import pytest
from flask import session

from auth_app.db import get_db

if TYPE_CHECKING:
    from flask.testing import FlaskClient, TestResponse


@dataclass
class RegistrationData:
    email: str
    name: str
    password: str


class TestRegister:
    @pytest.fixture
    def user_data(self) -> RegistrationData:
        return RegistrationData(email='123@email.com', name='123', password='123pwd')

    @staticmethod
    def test_should_add_record_to_database(client: FlaskClient, user_data: RegistrationData) -> None:
        with client:
            client.post('/register', data=asdict(user_data))

            user: sqlite3.Row = get_db().execute(
                'SELECT email, name FROM user WHERE email = ?', (user_data.email,)).fetchone()

            assert user['email'] == user_data.email
            assert user['name'] == user_data.name

    @staticmethod
    def test_should_redirect_to_login_if_succeeded(client: FlaskClient, user_data: RegistrationData) -> None:
        response: TestResponse = client.post(
            '/register', data=asdict(user_data))

        assert response.location == '/login'

    @staticmethod
    def test_should_stay_in_register_if_email_has_already_been_used(client: FlaskClient, user_data: RegistrationData) -> None:
        client.post('/register', data=asdict(user_data))

        response: TestResponse = client.post(
            '/register', data=asdict(user_data))

        assert response.location == '/register'


class TestLogin:
    @staticmethod
    def test_should_redirect_to_profile_if_succeeded(client: FlaskClient) -> None:
        response: TestResponse = client.post(
            '/login', data={'email': 'test@email.com', 'password': 'test'})

        assert response.location == '/profile'

    @staticmethod
    def test_should_stay_in_login_if_failed(client: FlaskClient) -> None:
        response: TestResponse = client.post(
            '/login', data={'email': 'someone@email.com', 'password': 'someone'})

        assert response.location == '/login'

    @staticmethod
    def test_should_add_user_id_and_name_into_session(client: FlaskClient) -> None:
        with client:
            client.post(
                '/login', data={'email': 'test@email.com', 'password': 'test'})

            user: sqlite3.Row = get_db().execute(
                'SELECT id FROM user WHERE email = "test@email.com"').fetchone()
            assert session['user_id'] == user['id']
            assert session['user_name'] == 'test'


class TestLogout:
    @staticmethod
    def test_should_be_login_required(client: FlaskClient) -> None:
        response: TestResponse = client.get('/logout')

        assert response.location == '/login'

    @staticmethod
    def test_should_clear_session(client: FlaskClient) -> None:
        with client:
            client.post(
                '/login', data={'email': 'test@email.com', 'password': 'test'})

            client.get('/logout')

            assert 'user_id' not in session
            assert 'user_name' not in session
