from __future__ import annotations
from typing import TYPE_CHECKING

from auth_app.models import User

if TYPE_CHECKING:
    from click.testing import Result
    from flask import Flask
    from flask.testing import FlaskCliRunner


def test_create_db_command(app: Flask, runner: FlaskCliRunner) -> None:
    with app.app_context():

        result: Result = runner.invoke(args=('create-db',))

    assert result.exit_code == 0
    assert result.output == 'Created the database.\n'


def test_repr_of_user() -> None:
    user = User(id=10, name='someone', email='someone@email.com', password='50me0nepwd')

    assert user.__repr__() == "User(id=10, email='someone@email.com', name='someone', password='50me0nepwd')"
