from __future__ import annotations
import sqlite3
from typing import TYPE_CHECKING, cast

import click
from flask import current_app, g

if TYPE_CHECKING:
    from flask import Flask


def init_app(app: Flask) -> None:
    app.cli.add_command(init_ab_command)
    app.teardown_appcontext(close_db)


@click.command('init-db')
def init_ab_command() -> None:
    init_db()
    click.echo('Initialized the database.')


def init_db() -> None:
    db: sqlite3.Connection = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


def get_db() -> sqlite3.Connection:
    if not _is_connection_created():
        _connect_db()
    return cast(sqlite3.Connection, g.db)


def close_db(e=None) -> None:
    if _is_connection_created():
        db = cast(sqlite3.Connection, g.pop('db'))
        db.close()


def _is_connection_created() -> bool:
    return 'db' in g


def _connect_db() -> None:
    g.db = sqlite3.connect(
        current_app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    g.db.row_factory = sqlite3.Row
