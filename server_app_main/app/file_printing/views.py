import time

from flask import session, g
from flask import redirect
from flask import render_template, url_for, current_app, request, send_from_directory, flash, jsonify
from . import file_printing
from .forms import *
from ..db_utils import *
from ..utils import *
from werkzeug.utils import secure_filename
import os
from flask_login import current_user, login_required
from wtforms import ValidationError
from ..utils.counters_of_pages import *
from .. import work_with_files

user_model_utils = UserModelUtils()
file_model_utils = FileModelUtils()
file_history_model_utils = FileHistoryModelUtils()
task_model_utils = TaskModelUtils()
task_history_model_utils = TaskHistoryModelUtils()
printer_model_utils = PrinterModelUtils()

"""
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=0.5)
"""

"""
@file_printing.route('/')
def choose_printer():
    ...


@file_printing.route('/upload_file')
def upload_file():
    print(current_app.config['UPLOAD_FOLDER'])
    return ''

"""


@file_printing.before_request
def check_choose_of_printer():
    # проверка того, что пользователь уже выбрал принтер, на котором будет печатать
    unique_printer_number = session.get('unique_printer_number')
    if unique_printer_number is None:
        return redirect(url_for('main.choose_printer'))

    printer = printer_model_utils.validate_printer_unique_number(unique_printer_number)
    if not printer or (not printer.ready_to_print):
        return redirect(url_for('main.choose_printer'))
    else:
        g.printer = printer


@file_printing.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Функция срабатывает, когда пользователь переходит на страницу для загрузки файлов для печати
    :return:
    """

    # если пользователь хочет изменить свой выбор по печати файлов, то нужно изменить статусы всех файлов таска
    # на waiting_to_be_added_to_the_task и удалить сам таск
    if not (session.get('task_id') is None):
        task_id = session.get('task_id')
        task = task_model_utils.validate_task(task_id, current_user.user_id)
        if task:
            """
            Если задача пользователя была выполнена (неважно как) или находится в процессе печати, то не нужно таск 
            удалять из бд и ничего менять в статусах, потому что это делается в rest части сервера. Нужно просто
            убрать значения из куки, чтобы обработать тот случай, когда пользователь хочет повторно напечатать что-то.
            
            Удаляем таск только в том случае, когда таск ожидал оплату, чтобы обработать изменения, которые пользователь
            проделает с задачей; или когда пользователь выбирал настройки печати.
            """
            if task.current_status in ['waiting_fielding_fields_of_printer_settings', 'waiting_for_payment_from_the_user']:
                file_model_utils.change_current_status_of_list_of_files(task.files,
                                                                        'waiting_to_be_added_to_the_task')
                task_model_utils.delete_task(task_id)
        session.pop('task_id')

    error_msg = ''
    upload_file_form = UploadFileForm()
    file_features = file_model_utils.get_file_features(current_user.files)
    return render_template('file_printing/upload_file.html', upload_file_form=upload_file_form,
                           file_features=file_features, error_msg=error_msg)


@file_printing.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    """
    Функция срабатывает, когда пользователь отправляет ajax запрос со страницы для загрузки файлов (file_printing.index)
    чтобы загрузить файл на сервер.
    :return:
    """
    # сначала считываем данные из формы, а уже потом проводим операции по возврату данных
    upload_file_form = UploadFileForm()

    """
    К этой функции поступают ajax запросы, для них также нужно осуществлять проверку на предмет того, что у пользователя
    не должно быть таска; если же он есть, то редиректим на file_printing.index, чтобы обнулить task_id
    """
    if not (session.get('task_id') is None):
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})

    error_msg = ''
    if upload_file_form.validate_on_submit():
        uploaded_file = upload_file_form.file.data
        try:
            upload_file_form.file_validator(uploaded_file)
        except ValidationError as exc:
            error_msg = str(exc)
            return jsonify(
                {'status': 'error',
                 'error_msg': error_msg})

        filename = uploaded_file.filename

        file = file_model_utils.add_new_file(current_user.user_id, filename, num_of_pages=-1)
        path_to_save = os.path.join(current_app.config['UPLOAD_PATH'], file.filename_server)
        uploaded_file.save(path_to_save)

        try:
            num_of_pages = get_num_of_pages_of_document(path_to_save, filename)
            if num_of_pages != 0:
                file = file_model_utils.change_num_of_pages(file, num_of_pages)
                file_features = file_model_utils.get_file_features(current_user.files)
                uploaded_file_collocation_name = file_features[0][0]

                file_history_model_utils.add_new_file_history(file.file_id, status='file_has_been_uploaded')
                file_history_model_utils.add_new_file_history(file.file_id,
                                                              status='waiting_to_be_added_to_the_task')
                return jsonify(
                    {'status': 'ok',
                     'html_element': render_template('file_printing/uploaded_area.html',
                                                     file_features=file_features),
                     'success_area': render_template('file_printing/success_area.html',
                                                     file_name=uploaded_file_collocation_name)})
            else:
                error_msg = 'FilePagesError'
        except Exception as err:
            error_msg = 'FilePagesError'

        file_model_utils.delete_file(file)
        work_with_files.delete_files([file.filename_server])

        return jsonify(
            {'status': 'error',
             'error_msg': error_msg})


@file_printing.route('/delete_file/<file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    """
    Когда пользователь на странице загрузки файлов (file_printing.index) нажимает кнопку удалить, то отправляется
    ajax запрос на сервер и эта функция обрабатывает этот ajax запрос.
    :param file_id:
    :return:
    """

    """
    К этой функции поступают ajax запросы, для них также нужно осуществлять проверку на предмет того, что у пользователя
    не должно быть таска; если же он есть, то редиректим на file_printing.index, чтобы обнулить task_id
    """
    if not (session.get('task_id') is None):
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})

    # если файл не найден или принадлежит другом пользователю, то возвращаем json ответ, который обновляет список задач
    filename = user_model_utils.del_user_file(current_user, int(file_id.strip()))
    if not filename:
        file_features = file_model_utils.get_file_features(current_user.files)
        return jsonify(
            {'status': 'error',
             'html_element': render_template('file_printing/uploaded_area.html', file_features=file_features)})

    # удаляем файл физически
    work_with_files.delete_files([filename])
    file_features = file_model_utils.get_file_features(current_user.files)
    return jsonify(
        {'status': 'ok',
         'html_element': render_template('file_printing/uploaded_area.html', file_features=file_features)})


@file_printing.route('/printer_settings', methods=['GET'])
@login_required
def printer_settings():
    """
    Функция срабатывает, когда пользователь переходит на страницу для настройки печати таска.
    :return:
    """

    """
    Если на момент настройки печати таска у пользователя уже есть таск в task_id, то редиректим его на начальную
    страницу чтобы сбросить таск.
    """
    if not (session.get('task_id') is None):
        return redirect(url_for('file_printing.index'))

    # создаем таск из задач пользователя, статус которых waiting_to_be_added_to_the_task
    list_of_files_for_adding_to_task = user_model_utils.get_list_of_files_that_waiting_to_be_added_to_the_task(
        current_user)
    if list_of_files_for_adding_to_task:
        task = task_model_utils.add_new_task(list_of_files_for_adding_to_task, user_id=current_user.user_id,
                                             printer_id=g.printer.printer_id)

        task_history_model_utils.add_new_task_history(task.task_id, 'task_has_been_created')
        task_history_model_utils.add_new_task_history(task.task_id, 'waiting_fielding_fields_of_printer_settings')

        file_history_model_utils.add_new_file_history_of_list_of_files(list_of_files_for_adding_to_task,
                                                                       'file_added_to_the_task')
        file_model_utils.change_current_status_of_list_of_files(list_of_files_for_adding_to_task,
                                                                'file_added_to_the_task')

        session['task_id'] = task.task_id
        file_features = file_model_utils.get_file_features(list_of_files_for_adding_to_task)
        return render_template('/file_printing/printer_settings.html', file_features=file_features, printer=g.printer,
                               num_of_pages_of_task=sum([file.num_of_pages for file in task.files]))
    else:
        return redirect(url_for('file_printing.index'))


@file_printing.route('/price_calculation', methods=['POST'])
@login_required
def price_calculation():
    """
    Функция срабатывает, когда пользователь на странице для настройки печати таска нажимает кнопку для рассчета цены
    таска после выбора всех настроек печати. Эта функция обрабатывает ajax запрос.
    :return:
    """

    """
    Если текущий таск пользователя невалидный, то редиректим его на начальную страницу, чтобы обнулить таск
    """
    task_id = session.get('task_id')
    if task_id is None:
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})
    task = task_model_utils.validate_task(task_id, current_user.user_id)
    if not task:
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})
    if task.current_status != 'waiting_fielding_fields_of_printer_settings':
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        params = request.json

        color_mode = params.get('color_printing_mode')
        flip_mode = params.get('flip_over_mode')
        num_of_copies = params.get('num_of_copies')
        if not all([isinstance(color_mode, bool), isinstance(flip_mode, bool), isinstance(num_of_copies, int)]):
            return jsonify({'status': 'type_of_printer_settings_data_error'})

        num_of_pages = sum([file.num_of_pages for file in task.files])

        # применяем скидку за двойную печать только к тем файлам, у которых больше одной страницы
        price = 0
        for file in task.files:
            price_per_file = 0
            if color_mode:
                price_per_file += file.num_of_pages * g.printer.price_per_page_for_color_printing_mode
            else:
                price_per_file += file.num_of_pages * g.printer.price_per_page_for_monochrome_printing_mode

            if flip_mode and file.num_of_pages > 1:
                price_per_file = round(price_per_file * ((100-g.printer.flip_over_printing_discount_in_percent) / 100), 2)

            price += price_per_file * num_of_copies

        # проверка того, что принтер сможет напечатать задачу
        min_num_of_pages_color = min(g.printer.num_of_pages_in_tray, g.printer.num_of_pages_of_color_cartridge)
        min_num_of_pages_monochrome = min(g.printer.num_of_pages_in_tray, g.printer.num_of_pages_of_cartridge)

        if color_mode:
            if flip_mode:
                if not (min_num_of_pages_color >= num_of_pages // 2):
                    return jsonify({'status': 'error',
                                    'html_element': render_template('/file_printing/lack_of_pages.html',
                                                                    num_of_pages_monochrome=min_num_of_pages_monochrome,
                                                                    num_of_pages_color=min_num_of_pages_color)})
                if num_of_pages < 2:
                    return jsonify({'status': 'error',
                                    'html_element': "<p>Перезагрузите страницу, возникла ошибка</p>"})
            else:
                if not (min_num_of_pages_color >= num_of_pages):
                    return jsonify({'status': 'error',
                                    'html_element': render_template('/file_printing/lack_of_pages.html',
                                                                    num_of_pages_monochrome=min_num_of_pages_monochrome,
                                                                    num_of_pages_color=min_num_of_pages_color)})
        else:
            if flip_mode:
                if not (min_num_of_pages_monochrome >= num_of_pages // 2):
                    return jsonify({'status': 'error',
                                    'html_element': render_template('/file_printing/lack_of_pages.html',
                                                                    num_of_pages_monochrome=min_num_of_pages_monochrome,
                                                                    num_of_pages_color=min_num_of_pages_color)})
            else:
                if not (min_num_of_pages_monochrome >= num_of_pages):
                    return jsonify({'status': 'error',
                                    'html_element': render_template('/file_printing/lack_of_pages.html',
                                                                    num_of_pages_monochrome=min_num_of_pages_monochrome,
                                                                    num_of_pages_color=min_num_of_pages_color)})

        task_model_utils.record_fields_of_printer_settings(task_id, num_of_pages, color_mode, flip_mode,
                                                           num_of_copies, price)
        flip_over_printing_discount_in_percent = None if not flip_mode else g.printer.flip_over_printing_discount_in_percent
        return jsonify({'status': 'ok', 'html_element': render_template('/file_printing/price_section.html',
                                                                        price=price, num_of_pages=num_of_pages*num_of_copies,
                                                                        flip_over_printing_discount_in_percent=flip_over_printing_discount_in_percent)})
    else:
        return jsonify({'status': 'content_type_error'})


@file_printing.route('/pay_for_the_task', methods=['GET'])
@login_required
def pay_for_the_task():
    """
    Функция срабатывает, когда пользователь переходит на страницу для оплаты таска.
    :return:
    """

    task_id = session.get('task_id')
    if task_id is None:
        return redirect(url_for('file_printing.index'))
    task = task_model_utils.validate_task(task_id, current_user.user_id)
    if not task:
        return redirect(url_for('file_printing.index'))
    """
    Если пользователь перезагрузит страницу, пока задача будет печататься или уже будет успешно или неуспешно завершена
    то его перекинет на страницу подраздел страницы история, где будет подробная информация о его задаче
    """
    if task.current_status in ['waiting_for_printing_to_start', 'printing_in_process', 'successfully_printed', 'occurred_error_while_printing']:
        return redirect(url_for('main.history'))
    if task.current_status != 'waiting_fielding_fields_of_printer_settings':
        return redirect(url_for('file_printing.index'))

    # меняем статус таска на waiting_for_payment_from_the_user
    task_model_utils.change_task_current_status(task, 'waiting_for_payment_from_the_user')
    task_history_model_utils.add_new_task_history(task.task_id, 'waiting_for_payment_from_the_user')

    file_model_utils.change_current_status_of_list_of_files(task.files, 'waiting_for_payment_from_the_user')
    file_history_model_utils.add_new_file_history_of_list_of_files(task.files, 'waiting_for_payment_from_the_user')

    return render_template('/file_printing/pay_for_the_task.html', url_for_support='https://t.me/great_death')


@file_printing.route('/print_task', methods=['GET'])
@login_required
def print_task():
    """
    Функция срабатывает, когда пользователь со страницы для оплаты таска (file_printing.pay_for_the_task) оплачивает
    таск и отправляет запрос на сервер для начала печати таска.
    :return:
    """

    task_id = session.get('task_id')
    if task_id is None:
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})
    task = task_model_utils.validate_task(task_id, current_user.user_id)
    if not task:
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})

    # если статус таска пользователя не соответствуюет текущему этапу, то отправляем пользователя на начальную страницу
    # чтобы сбросить значение таска
    if task.current_status != 'waiting_for_payment_from_the_user':
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})

    task_model_utils.change_task_current_status(task, 'waiting_for_printing_to_start')
    task_history_model_utils.add_new_task_history(task.task_id, 'waiting_for_printing_to_start')

    file_model_utils.change_current_status_of_list_of_files(task.files, 'waiting_for_printing_to_start')
    file_history_model_utils.add_new_file_history_of_list_of_files(task.files, 'waiting_for_printing_to_start')

    return jsonify({'status': 'ok'})


@file_printing.route('/get_info_about_printing_task', methods=['GET'])
@login_required
def get_info_about_printing_task():
    task_id = session.get('task_id')
    if task_id is None:
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})
    task = task_model_utils.validate_task(task_id, current_user.user_id)
    if not task:
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})

    # если статус таска пользователя не соответствуюет текущему этапу, то отправляем пользователя на начальную страницу
    # чтобы сбросить значение таска
    if task.current_status not in ['waiting_for_printing_to_start', 'printing_in_process', 'successfully_printed', 'occurred_error_while_printing']:
        return jsonify({'status': 'redirect', 'link': url_for('file_printing.index')})

    if task.current_status == 'successfully_printed':
        return jsonify({'status': 'successfully_printed'})
    elif task.current_status == 'occurred_error_while_printing':
        return jsonify({'status': 'occurred_error_while_printing'})
    else:
        return jsonify({'status': 'printing_in_process'})


