from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return '<h1>Ошибка 404</h1>', 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return '<h1>Ошибка 500</h1>', 500