import os
from secrets import token_hex
from typing import Mapping, Optional

from flask import Flask

from auth_app import db


def create_app(test_config: Optional[Mapping] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=token_hex(),
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    from auth_app import auth, main

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
