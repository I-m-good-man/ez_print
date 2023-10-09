from flask import session, send_file, jsonify
from flask import redirect
from flask import render_template, url_for, current_app, request
from . import rest_printer_api
from .forms import *
from ..db_utils import *
from werkzeug.utils import secure_filename
import os
from flask_login import current_user, login_user
from flask import request, make_response
import flask_restful as restful
import time
from ..work_with_files import get_archive_of_files, NotAllFilesExist, delete_files
from ..utils import json_object
from ..work_with_files import delete_files


task_model_utils = TaskModelUtils()
task_history_model_utils = TaskHistoryModelUtils()
file_model_utils = FileModelUtils()
file_history_model_utils = FileHistoryModelUtils()
printer_model_utils = PrinterModelUtils()
printer_history_model_utils = PrinterHistoryModelUtils()


@rest_printer_api.route('/printer_api/task/get_task_for_printing', methods=['POST'])
def get_task_for_printing():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        params = request.json
        printer_id = params.get('printer_id')
        secret_key = params.get('secret_key')
        ready_to_print = params.get('ready_to_print')
        num_of_pages_in_tray = params.get('num_of_pages_in_tray')
        num_of_pages_of_cartridge = params.get('num_of_pages_of_cartridge')
        num_of_pages_of_color_cartridge = params.get('num_of_pages_of_color_cartridge')
        for param in [printer_id, secret_key, ready_to_print, num_of_pages_in_tray, num_of_pages_of_cartridge, num_of_pages_of_color_cartridge]:
            # пришли не все необходимые данные
            if param is None:
                data = {'status': 'error', 'type': 'not_all_properties_had_sent'}
                return make_response(jsonify(data), 400)

        # если принтер не провалидировался, то отправляем соответствующйи ответ
        printer = printer_model_utils.validate_printer(printer_id, secret_key)
        if not printer:
            data = {'status': 'error', 'type': 'invalid_printer'}
            return make_response(jsonify(data), 400)

        # время последней активности до его обновления
        last_last_date_of_printer_activity = printer.last_date_of_activity

        # обновляем данные о последней дате активности принтера
        printer_model_utils.update_last_date_of_activity(printer)

        # времени прошло со времени последней активности принтера
        delta = printer.last_date_of_activity - last_last_date_of_printer_activity

        # если сервер установил ready_to_print=False из-за того, что сигнал не поступал от принтера 10 минут и вот
        # сигнал от принтера пришел
        # if printer.status == 'lost_connection_to_printer':
        #     printer_model_utils.change_status(printer, 'ok')

        # обновляем значения для принтера
        printer_model_utils.update_volatile_fields_of_printer(printer_id, ready_to_print, num_of_pages_in_tray, num_of_pages_of_cartridge, num_of_pages_of_color_cartridge)

        # в течение 50 секунд ожидаем появления задачи для принтера
        for i in range(50):
            task = task_model_utils.fetch_active_task_for_printer(printer_id)
            if task is None:
                time.sleep(1)
            else:
                task_model_utils.change_task_current_status(task, 'printing_in_process')
                task_history_model_utils.add_new_task_history(task.task_id, 'printing_in_process')

                file_model_utils.change_current_status_of_list_of_files(task.files, 'printing_in_process')
                file_history_model_utils.add_new_file_history_of_list_of_files(task.files,
                                                                               'printing_in_process')

                printer_history_model_utils.add_new_printer_history(printer_id, f'task_id={task.task_id}; ok; has sent to printing')

                filenames = [file.filename_server for file in task.files]
                try:
                    json_properties = json_object.get_msg_for_dispatch_of_files(printer_id, secret_key, task.task_id,
                                                                                task.num_of_pages, task.color_mode,
                                                                                task.flip_mode, task.num_of_copies, filenames)
                    stream = get_archive_of_files(filenames, json_properties)

                except NotAllFilesExist:
                    # возвращаем ошибку о том, что нет задач, потому что какой то из файлов еще не сохранился
                    data = {'status': 'error', 'type': 'not_all_user_files_had_uploaded'}
                    return make_response(jsonify(data), 400)

                # удаляем отправляемые файлы с сервера
                delete_files(filenames)

                # ставим статусы файлам, что они удалены
                file_model_utils.change_current_status_of_list_of_files(task.files, 'deleted')
                file_history_model_utils.add_new_file_history_of_list_of_files(task.files, 'deleted')

                return send_file(
                    stream,
                    as_attachment=True,
                    attachment_filename=f'{task.task_id}.zip'
                )

        printer_history_model_utils.add_new_printer_history(printer_id, 'task_id=-1; ok; not_found_new_tasks_for_printer')
        # отправляем данные о том, что новых задач для принтера нет
        data = {'status': 'ok', 'type': 'not_found_new_tasks_for_printer'}
        return make_response(jsonify(data), 200)
    else:
        # пришли не json данные
        data = {'status': 'error', 'type': 'not_json_data_had_sent'}
        return make_response(jsonify(data), 400)


@rest_printer_api.route('/printer_api/task/successfully_printed', methods=['POST'])
def successfully_printed():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        params = request.json
        printer_id = params.get('printer_id')
        secret_key = params.get('secret_key')
        task_id = params.get('task_id')

        for param in [printer_id, secret_key, task_id]:
            # пришли не все необходимые данные
            if param is None:
                data = {'status': 'error', 'type': 'not_all_properties_had_sent'}
                return make_response(jsonify(data), 400)

        # если принтер не провалидировался, то отправляем соответствующйи ответ
        printer = printer_model_utils.validate_printer(printer_id, secret_key)
        if not printer:
            data = {'status': 'error', 'type': 'invalid_printer'}
            return make_response(jsonify(data), 400)

        # обновляем данные о последней дате активности принтера
        printer_model_utils.update_last_date_of_activity(printer)

        task = task_model_utils.get_task(task_id)
        if not task:
            data = {'status': 'error', 'type': 'task_doesnt_exist'}
            return make_response(jsonify(data), 400)
        if not task.current_status == 'printing_in_process':
            data = {'status': 'error', 'type': 'error_of_task_current_status'}
            return make_response(jsonify(data), 400)

        task_model_utils.change_task_current_status(task, 'successfully_printed')
        task_history_model_utils.add_new_task_history(task.task_id, 'successfully_printed')

        printer_history_model_utils.add_new_printer_history(printer_id, f'task_id={task.task_id}; ok; successfully_printed')

        data = {'status': 'ok', 'type': 'changes_applied'}
        return make_response(jsonify(data), 200)
    else:
        # пришли не json данные
        data = {'status': 'error', 'type': 'not_json_data_had_sent'}
        return make_response(jsonify(data), 400)


@rest_printer_api.route('/printer_api/task/error', methods=['POST'])
def occurred_error_while_printing():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        params = request.json
        printer_id = params.get('printer_id')
        secret_key = params.get('secret_key')
        task_id = params.get('task_id')
        error_text = params.get('error_text')
        for param in [printer_id, secret_key, task_id, error_text]:
            # пришли не все необходимые данные
            if param is None:
                data = {'status': 'error', 'type': 'not_all_properties_had_sent'}
                return make_response(jsonify(data), 400)

        # если принтер не провалидировался, то отправляем соответствующйи ответ
        printer = printer_model_utils.validate_printer(printer_id, secret_key)
        if not printer:
            data = {'status': 'error', 'type': 'invalid_printer'}
            return make_response(jsonify(data), 400)

        # обновляем данные о последней дате активности принтера
        printer_model_utils.update_last_date_of_activity(printer)

        task = task_model_utils.get_task(task_id)
        if not task:
            data = {'status': 'error', 'type': 'task_doesnt_exist'}
            return make_response(jsonify(data), 400)
        if not task.current_status == 'printing_in_process':
            data = {'status': 'error', 'type': 'error_of_task_current_status'}
            return make_response(jsonify(data), 400)

        task_model_utils.change_task_current_status(task, 'occurred_error_while_printing')
        task_history_model_utils.add_new_task_history(task.task_id, 'occurred_error_while_printing')

        printer_history_model_utils.add_new_printer_history(printer_id, f'task_id={task.task_id}; error; {error_text}')

        data = {'status': 'ok', 'type': 'error_handled'}
        return make_response(jsonify(data), 200)
    else:
        # пришли не json данные
        data = {'status': 'error', 'type': 'not_json_data_had_sent'}
        return make_response(jsonify(data), 400)




