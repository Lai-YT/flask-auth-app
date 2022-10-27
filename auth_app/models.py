import click
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

from auth_app.db import db


class User(db.Model, UserMixin):  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    password: Mapped[str]

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, email={self.email!r}, name={self.name!r}, password={self.password!r})'


def create_db() -> None:
    with current_app.app_context():
        db.create_all()


@click.command('create-db')
def create_db_command() -> None:
    create_db()
    click.echo('Created the database.')
