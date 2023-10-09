from flask import Blueprint

rest_printer_api = Blueprint('rest_printer_api', __name__)

from . import views, errors