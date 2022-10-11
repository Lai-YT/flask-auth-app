from flask import Blueprint, render_template, session

from auth_app.auth import login_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=session['user_name'])
