from flask import session
from flask import redirect
from flask import render_template, url_for, current_app, request
from . import admin
from .forms import *
from ..db_utils import UserModelUtils
from werkzeug.utils import secure_filename
import os
from flask_login import current_user, login_user
from flask import request


user_mode_utils = UserModelUtils()


@admin.route('/')
def index():
    return ''



