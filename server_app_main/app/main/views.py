from flask import session
from flask import redirect, request
from flask import render_template, url_for, jsonify
from . import main
from .forms import *
from ..db_utils import *
from flask_login import login_required
from flask_login import current_user, login_required


"""
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=0.5)
"""


printer_model_utils = PrinterModelUtils()
task_model_utils = TaskModelUtils()
file_model_utils = FileModelUtils()



@main.route('/')
@login_required
def index():
    return render_template(r'/main/index.html')


@main.route('/choose_printer')
@login_required
def choose_printer():
    """
    Если пользователь решит сменить принтер, то нажав на кнопку выбрать принтер он перейдет на file_printing.index и
    там будет обработка текущего статуса задачи пользователя
    """
    batch_of_printers = printer_model_utils.get_batch_of_printers(1)
    srcs_to_img_of_printer = ['/photos_of_printer/'+printer_model_utils.get_src_of_main_photo_of_printer(printer) for printer in batch_of_printers]

    return render_template(r'/main/choose_printer.html', batch_of_printers_and_srcs_to_img_of_printer=list(zip(batch_of_printers, srcs_to_img_of_printer)))


@main.route('/choose_printer/get_batch_of_printers', methods=['POST'])
@login_required
def get_new_batch_of_printers():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        params = request.json
        num_of_batch = params.get('num_of_batch')
        if not isinstance(num_of_batch, int):
            return jsonify(
                {'status': 'error'})
        batch_of_printers = printer_model_utils.get_batch_of_printers(num_of_batch)
        srcs_to_img_of_printer = ['/photos_of_printer/'+printer_model_utils.get_src_of_main_photo_of_printer(printer) for printer in batch_of_printers]
        if batch_of_printers:
            return jsonify(
                {'status': 'ok',
                 'html_element': render_template('main/batch_of_printers.html', batch_of_printers_and_srcs_to_img_of_printer=list(zip(batch_of_printers, srcs_to_img_of_printer)))})
        return jsonify(
            {'status': 'error'})


@main.route('/choose_num_of_printer/<unique_printer_number>')
@login_required
def choose_num_of_printer_handler(unique_printer_number):
    session['unique_printer_number'] = unique_printer_number
    return redirect(url_for('file_printing.index'))


@main.route('/available_extensions')
def available_extensions():
    return render_template('/main/available_extensions.html',
                           extensions=current_app.config['ALLOWED_EXTENSIONS'])

@main.route('/history')
def history():
    return render_template(r'/main/undone_section.html')


@main.route('/support')
def support():
    return render_template(r'/main/undone_section.html')


@main.route('/discounts')
def discounts():
    return render_template(r'/main/undone_section.html')


@main.route('/about_project')
def about_project():
    return render_template(r'/main/undone_section.html')


@main.route('/policy')
def policy():
    return render_template(r'/main/undone_section.html')


@main.route('/company_info')
def company_info():
    return render_template(r'/main/undone_section.html')






