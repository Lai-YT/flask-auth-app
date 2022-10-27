from secrets import token_hex
from typing import Mapping, Optional

from flask import Flask
from flask_login import LoginManager

from auth_app import auth, main
from auth_app.db import db
from auth_app.models import User, create_db_command


def create_app(test_config: Optional[Mapping] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=token_hex(),
        SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite',
        SQLALCHEMY_ECHO=True,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    app.cli.add_command(create_db_command)
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    login_manager = LoginManager()
    login_manager.init_app(app)

    auth.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        return db.session.get(User, user_id)

    return app
