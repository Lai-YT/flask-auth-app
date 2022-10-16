import functools
from typing import Callable, Optional

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from auth_app.db import db
from auth_app.models import User

bp = Blueprint('auth', __name__)


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
    session.clear()
    session['user_id'] = user.id
    session['user_name'] = user.name
    return redirect(url_for('main.profile'))


@bp.before_app_request
def load_logged_in_user() -> None:
    try:
        user_id: int = session['user_id']
        stmt: Select = db.select(User).where(User.id == user_id)
        g.user = db.session.execute(stmt).scalars().one()
    except KeyError:
        g.user = None


def login_required(view: Callable):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/logout')
@login_required
def logout():
    session.clear()
    return render_template('index.html')
