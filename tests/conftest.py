from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Generator

import pytest

from auth_app import create_app
from auth_app.db import db
from auth_app.models import create_db

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient, FlaskCliRunner

data_sql: str = (Path(__file__).parent / 'data.sql').read_text('utf-8')


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app: Flask = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_ECHO': False,
    })
    with app.app_context():
        create_db()
        db.session.execute(db.text(data_sql))
        db.session.commit()

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
