from . import db
from flask_login import UserMixin
from itsdangerous import URLSafeSerializer
from flask import current_app
import os
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from datetime import datetime


task_to_file_association_table = db.Table(
    'task_to_file_association_table',
    db.Model.metadata,
    db.Column('task_id', db.ForeignKey('tasks.task_id')),
    db.Column('file_id', db.ForeignKey('files.file_id')),
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_id_hash = db.Column(db.Text, unique=True)

    files = db.relationship('File', back_populates='user', uselist=True)
    tasks = db.relationship('Task', back_populates='user', uselist=True)

    def get_id(self):
        return self.user_id_hash

    def add_user_id_hash(self):
        s = URLSafeSerializer(current_app.config['SECRET_KEY'])
        self.user_id_hash = s.dumps(self.user_id)

    def decode_user_id_hash(self, user_id_hash):
        s = URLSafeSerializer(current_app.config['SECRET_KEY'])
        return s.loads(user_id_hash)


class File(db.Model):
    """
    current_status:
        file_has_been_uploaded - файл был загружен
        waiting_to_be_added_to_the_task - файл ждет, чтобы его добавили в новую задачу
        file_added_to_the_task - файл добавили в задачу
        printing_in_process - файл печатается
        deleted - файл удален
    """
    __tablename__ = 'files'
    file_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date_of_save = db.Column(db.DateTime(), default=datetime.utcnow)
    filename_server = db.Column(db.Text, unique=True)
    filename_user = db.Column(db.Text)
    num_of_pages = db.Column(db.Integer)
    current_status = db.Column(db.String, default='waiting_to_be_added_to_the_task')

    user = db.relationship('User', back_populates='files', uselist=False)
    task = db.relationship('Task', secondary=task_to_file_association_table, uselist=False, back_populates='files')
    file_history = db.relationship('FileHistory', back_populates='file', uselist=True)


    def add_filename_server(self):
        extension = self.filename_user.split('.')[-1]
        filename_server = f'{self.user.user_id}_{self.file_id}.{extension}'
        self.filename_server = filename_server


class FileHistory(db.Model):
    """
    Поле status может принимать следующие значения:
    downloaded_to_server
    deleted_from_server
    """
    __tablename__ = 'files_history'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.file_id'))
    date_of_change = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.String)

    file = db.relationship('File', back_populates='file_history', uselist=False)


class Task(db.Model):

    """
    flip_mode: 1-no flip, 2-flip up, 3-flip over
    color_mode: 1-color, 2-monochrome
    num_of_copies: ...

    current_status:
        task_has_been_created - задача была успешно создана
        waiting_fielding_fields_of_printer_settings - ждет заполнения полей настройки печати
        waiting_for_payment_from_the_user - ожидается оплата от пользователя
        waiting_for_printing_to_start - ждет начала печати
        printing_in_process - печать в процессе
        occurred_error_while_printing - произошла ошибка во время печати
        successfully_printed - задача успешно напечатана
    """
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    printer_id = db.Column(db.Integer, db.ForeignKey('printers.printer_id'))
    num_of_pages = db.Column(db.Integer)
    color_mode = db.Column(db.Integer)
    flip_mode = db.Column(db.Integer)
    num_of_copies = db.Column(db.Integer)
    current_status = db.Column(db.String, default='waiting_fielding_fields_of_printer_settings')
    price = db.Column(db.Float)

    user = db.relationship('User', back_populates='tasks', uselist=False)
    files = db.relationship('File', secondary=task_to_file_association_table, uselist=True, back_populates='task')
    tasks_history = db.relationship('TaskHistory', back_populates='task', uselist=True)
    printer = db.relationship('Printer', back_populates='tasks', uselist=False)


class TaskHistory(db.Model):
    """
    Поле status может принимать следующие значения:
    downloaded_on_server
    sent_to_printer
    has_printed
    """
    __tablename__ = 'tasks_history'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    date_of_change = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.String)

    task = db.relationship('Task', back_populates='tasks_history', uselist=False)


class Printer(db.Model):
    """
    Возможные значения поля status:
    ok - принтер работает в штатном режиме
    lost_connection_to_printer - соединение с принтером потеряно, когда принтер более 10 минут не связывался с сервером
    printer_error - ошибка принтера - когда принтер сам определил ошибку своей работы и сообщил об этом серверу
    printer_in_service - принтер находится  на обслуживании - решается проблема или меняются расходники
    waiting_for_information_update - принтер ждет обновления информации, т.е. сервер ждет отправки на принтер респонса
    с инфой о том, что ему в конфиге нужно обновить
    """
    __tablename__ = 'printers'
    printer_id = db.Column(db.Integer, primary_key=True, index=True)
    secret_key = db.Column(db.String)
    ready_to_print = db.Column(db.Boolean)
    status = db.Column(db.String, default='ok')
    num_of_pages_in_tray = db.Column(db.Integer)
    num_of_pages_of_cartridge = db.Column(db.Integer)
    num_of_pages_of_color_cartridge = db.Column(db.Integer)
    monochrome_printing_mode = db.Column(db.Boolean)
    color_printing_mode = db.Column(db.Boolean)
    no_flip_mode = db.Column(db.Boolean)
    flip_up_mode = db.Column(db.Boolean)
    flip_over_mode = db.Column(db.Boolean)
    flip_over_printing_discount_in_percent = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    unique_number = db.Column(db.Integer, index=True)
    price_per_page_for_monochrome_printing_mode = db.Column(db.Integer)
    price_per_page_for_color_printing_mode = db.Column(db.Integer)
    can_scan = db.Column(db.Boolean)
    last_date_of_activity = db.Column(db.DateTime(), default=datetime.utcnow)

    tasks = db.relationship('Task', uselist=True, back_populates='printer')
    location = db.relationship('Location', back_populates='printer', uselist=False)
    printer_history = db.relationship('PrinterHistory', back_populates='printer', uselist=True)


class PrinterHistory(db.Model):
    """
    status - статус принтера, может принимать значения:
    jam_in_tray - замятие в лотке
    cartridge_is_ended - кончился картридж
    tray_is_empty - кончилась бумага в лотке
    """
    __tablename__ = 'printers_history'
    id = db.Column(db.Integer, primary_key=True)
    printer_id = db.Column(db.Integer, db.ForeignKey('printers.printer_id'))
    date_of_change = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.String)

    printer = db.relationship('Printer', back_populates='printer_history', uselist=False)


class Location(db.Model):
    """
    Поле status может принимать следующие значения:
    downloaded_on_server
    sent_to_printer
    has_printed
    """
    __tablename__ = 'locations'
    location_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text)
    description = db.Column(db.Text)

    printer = db.relationship('Printer', back_populates='location', uselist=False)
    photos = db.relationship('Photo', back_populates='location', uselist=True)


class Photo(db.Model):
    """
    num_of_photo - номер фото, чтобы можно было определять порядок, в котором фотки должны показываться пользователю
    """
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    src_to_img = db.Column(db.String)
    num_of_photo = db.Column(db.Integer)

    location = db.relationship('Location', back_populates='photos', uselist=False)


def models_test():
    user1 = User(user_id=123, user_id_hash=456)
    user2 = User(user_id=456, user_id_hash=789)

    file1 = File(user_id=123, filename_server='1.docx', filename_user='aaa.docx', num_of_pages=5)
    file2 = File(user_id=123, filename_server='2.docx', filename_user='bbb.docx', num_of_pages=1)
    file3 = File(user_id=456, filename_server='5.docx', filename_user='df.docx', num_of_pages=5)

    task1 = Task(user_id=123, num_of_pages=file1.num_of_pages+file2.num_of_pages, price=10)
    task1.files.append(file1)
    task1.files.append(file2)

    task2 = Task(user_id=456, num_of_pages=file3.num_of_pages, price=20)
    task2.files.append(file3)

    db.session.add_all([user1, user2, file1, file2, file3, task1, task2])
    db.session.commit()








