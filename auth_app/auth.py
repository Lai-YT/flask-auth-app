from typing import Optional

from flask import (Blueprint, Flask, flash, redirect, render_template, request,
                   url_for)
from flask_login import login_required, login_user, logout_user, set_login_view
from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from auth_app.db import db
from auth_app.models import User

bp = Blueprint('auth', __name__)


def init_app(app: Flask) -> None:
    """Should be called after the LoginManager is set."""
    with app.app_context():
        set_login_view(f'{bp.name}.login')


@bp.route('/login')
def login():
    return render_template('login.html')


@bp.route('/register')
def register():
    return render_template('register.html')


@bp.route('/register', methods=['POST'])
def register_post():
    """Redirects to the login page if registrated successfully;
    otherwise keeps in the registration page.
    """
    email: str = request.form['email']
    name: str = request.form['name']
    password: str = request.form['password']

    try:
        db.session.add(User(email=email, name=name, password=generate_password_hash(password)))
        db.session.commit()
        return redirect(url_for('auth.login'))
    except IntegrityError:
        flash('Email address already registered.')
        return redirect(url_for('auth.register'))


@bp.route('/login', methods=['POST'])
def login_post():
    """Redirects to the profile page if logged in successfully;
    otherwise keeps in the login page.
    """
    email: str = request.form['email']
    password: str = request.form['password']

    stmt: Select = db.select(User).where(User.email == email)
    user: Optional[User] = db.session.execute(stmt).scalars().one_or_none()
    if user is None or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    login_user(user)
    return redirect(url_for('main.profile'))


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')
