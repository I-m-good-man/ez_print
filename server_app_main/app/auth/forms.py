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
    file = FileField(validators=[FileRequired()])
    submit = SubmitField('Submit')

    def validate_file(self, file):
        file = self.file.data
        # Extension check
        extension = file.filename.lower().split('.')[-1]
        if extension not in current_app.config['ALLOWED_EXTENSIONS']:
            raise ValidationError('Invalid extension of file!')

        # File size check
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        if file_size > current_app.config['MAX_UPLOAD_SIZE']:
            raise ValidationError('50 Mb maximum!')





