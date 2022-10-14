from __future__ import annotations
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Generator

import pytest

from auth_app import create_app
from auth_app.db import get_db, init_db

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient, FlaskCliRunner

data_sql: str = (Path(__file__).parent / 'data.sql').read_text('utf-8')


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    db_fd, db_path = tempfile.mkstemp()

    app: Flask = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
