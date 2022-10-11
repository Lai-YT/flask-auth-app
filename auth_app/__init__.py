import os
from secrets import token_hex

from flask import Flask

from auth_app import db


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=token_hex(),
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    db.init_app(app)

    from auth_app import auth, main

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
