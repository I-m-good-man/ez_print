from flask import session
from flask import redirect
from flask import render_template, url_for, current_app, request
from . import auth
from .forms import *
from ..db_utils import UserModelUtils
from werkzeug.utils import secure_filename
import os
from flask_login import current_user, login_user
from flask import request


user_mode_utils = UserModelUtils()


@auth.route('/login')
def login():
    if current_user.is_anonymous:
        new_user = user_mode_utils.add_new_user()
        login_user(new_user, True)

    next_url = request.args.get('next')
    if next_url is None or not next_url.startswith('/'):
        next_url = url_for('main.index')
    return redirect(next_url)



