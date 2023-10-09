from flask import Blueprint

file_printing = Blueprint('file_printing', __name__)

from . import views, errors