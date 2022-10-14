import functools
import sqlite3
from typing import Callable

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from auth_app.db import get_db

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
        with get_db() as db:
            db.execute(
                'INSERT INTO user (email, name, password) VALUES (?, ?, ?)',
                (email, name, generate_password_hash(password))
            )
    except sqlite3.IntegrityError:
        flash('Email address already registered.')
        return redirect(url_for('auth.register'))
    else:
        return redirect(url_for('auth.login'))


@bp.route('/login', methods=['POST'])
def login_post():
    """Redirects to the profile page if logged in successfully;
    otherwise keeps in the login page.
    """
    email: str = request.form['email']
    password: str = request.form['password']

    user = get_db().execute('SELECT * FROM user WHERE email = ?',
                            (email,)).fetchone()
    if user is None or not check_password_hash(user['password'], password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    session.clear()
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    return redirect(url_for('main.profile'))


@bp.before_app_request
def load_logged_in_user() -> None:
    try:
        user_id = session['user_id']
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
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
