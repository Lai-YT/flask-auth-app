from __future__ import annotations
from typing import TYPE_CHECKING

import pytest
from flask import session
from sqlalchemy import Select

from auth_app.db import db
from auth_app.models import User

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from werkzeug.test import TestResponse


class TestRegister:
    @pytest.fixture
    def user_data(self) -> User:
        return User(email='123@email.com', name='123', password='123pwd')

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
    def test_should_stay_in_register_if_email_has_already_been_used(
            client: FlaskClient, user_data: User) -> None:
        client.post('/register', data=user_data.__dict__)

        response: TestResponse = client.post('/register', data=user_data.__dict__)

        assert response.location == '/register'


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
    def test_should_stay_in_login_if_failed(client: FlaskClient) -> None:
        response: TestResponse = client.post(
            '/login',
            data={
                'email': 'someone@email.com',
                'password': 'someone'})

        assert response.location == '/login'

    @staticmethod
    def test_should_add_user_id_and_name_into_session(client: FlaskClient) -> None:
        with client:
            client.post('/login', data={'email': 'test@email.com', 'password': 'test'})

            stmt: Select = db.select(User.id).where(User.email == 'test@email.com')
            user_id: int = db.session.execute(stmt).scalars().first()
            assert session['user_id'] == user_id
            assert session['user_name'] == 'test'


class TestLogout:
    @staticmethod
    def test_should_be_login_required(client: FlaskClient) -> None:
        response: TestResponse = client.get('/logout')

        assert response.location == '/login'

    @staticmethod
    def test_should_clear_session(client: FlaskClient) -> None:
        with client:
            client.post('/login', data={'email': 'test@email.com', 'password': 'test'})

            client.get('/logout')

            assert 'user_id' not in session
            assert 'user_name' not in session
