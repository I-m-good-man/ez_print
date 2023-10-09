from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from flask import current_app, request
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import ValidationError


"""
FileRequired - проверяет, что загрузили файл
FileAllowed - проверяет, что формат файла - один из тех, что указаны в переданном в него списке.
"""
class UploadFileForm(FlaskForm):
    file = FileField('file', validators=[FileRequired()])
    submit = SubmitField()

    @staticmethod
    def file_validator(file):
        # Extension check
        extension = file.filename.lower().split('.')[-1]
        if extension not in current_app.config['ALLOWED_EXTENSIONS']:
            raise ValidationError('FileExtensionError')

        # File size check
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        if file_size > current_app.config['MAX_UPLOAD_SIZE']:
            raise ValidationError('FileSizeError')




