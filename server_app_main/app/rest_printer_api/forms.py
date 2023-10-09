from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from flask import current_app, request
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import ValidationError


"""
FileRequired - проверяет, что загрузили файл
FileAllowed - проверяет, что формат файла - один из тех, что указаны в переданном в него списке.
"""






