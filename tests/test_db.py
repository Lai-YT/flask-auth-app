from __future__ import annotations
import sqlite3
from typing import TYPE_CHECKING

import pytest

from auth_app.db import get_db


if TYPE_CHECKING:
    from click.testing import Result
    from flask import Flask
    from flask.testing import FlaskCliRunner


def test_get_db_during_a_request_should_be_the_same(app: Flask) -> None:
    with app.app_context():
        db: sqlite3.Connection = get_db()

        assert get_db() == db


def test_db_should_be_closed_ath_the_end_of_request(app: Flask) -> None:
    with app.app_context():
        db: sqlite3.Connection = get_db()

    with pytest.raises(sqlite3.ProgrammingError, match='closed'):
        db.execute('')


def test_init_db_command_should_init_db(app: Flask, runner: FlaskCliRunner) -> None:
    with app.app_context():
        runner.invoke(args=('init-db',))

        row: sqlite3.Row = get_db().execute('SELECT COUNT(*) as count FROM user').fetchone()
    assert row['count'] == 0


def test_init_db_command_should_output_message(app: Flask, runner: FlaskCliRunner) -> None:
    with app.app_context():
        result: Result = runner.invoke(args=('init-db',))

    assert 'Initialized the database.' in result.output
