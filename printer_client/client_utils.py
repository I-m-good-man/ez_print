import json
import os
import time

import requests
import zipfile, io
import shutil
import threading
from print_docs.task_utils import Task



"""
Request запросы делятся на следующие типы:

1)  POST запрос на url /printer_api/task/get_task_for_printing - long-poll запрос, который запрашивает у сервера задачу для печати

    Request args:  
    - printer_id - идентификатор принтера
    - secret_key - секретный ключ, который известен только принтеру и серверу
    - ready_to_print - статус принтера, который сообщает о готовности принтера печатать
    - num_of_pages_in_tray - количество страниц в лотке
    - num_of_pages_of_cartridge - количество страниц, которые может распечатать картридж
    
    Response args in json document:
    - printer_id - идентификатор принтера
    - secret_key - секретный ключ, который известен только принтеру и серверу
    - task_id - номер задачи
    - num_of_pages_of_document - количество страниц в документах суммарно
    - color_mode - цветная или ч/б печать - смотреть спецификацию метода print_file класса PMFuncs
    - flip_mode - нужно ли печатать в двухстраничном режиме - см выше
    - num_of_copies - количество копий документа, которые нужно распечатать - см выше
    
2)  POST запрос на url /printer_api/task/error - информирует сервер о том, что произошла какая-то ошибка при печати.

    Request args:
    - printer_id - идентификатор принтера
    - secret_key - секретный ключ, который известен только принтеру и серверу      
    - task_id - номер задачи, при выполнении которой возникла ошибка
    - error_text - текст ошибки
    
    Response args:
    - num_of_action_script - номер сценарий действий
    

3)  GET запрос на url /printer_api/task/successfully_printed - запрос информирует о том, что файл был распечатан без проблем

    Request args:
    - printer_id - идентификатор принтера
    - secret_key - секретный ключ, который известен только принтеру и серверу      
    - task_id - номер задачи, которая была успешно выполнена
    
    Response args:
        Status: error
        type: 
            not_all_properties_had_sent - принтер отправил не все данные в request'e
            invalid_printer - принтер указал невалидные для логинизации принтера
            task_doesnt_exist - задачи, которую указал принтер в запросе, не существует
            error_of_task_current_status - задача, которая успешно завершена, имеет статус не printing_in_process
            not_json_data_had_sent - принтер отправил не json данные
        
        Status: ok
        type: 
            changes_applied - информация об успешной работе успешно обработана
        
"""

class ConfigProperty:
    """
    Класс для реализации потоко-безопасных дескрипторов изменяемых свойств конфигурации принтера.
    """
    def __init__(self, param_name):
        self.param_name = param_name

    def __get__(self, instance, owner):
        with instance.property_lock:
            res = instance._get_config_dict(instance.path).get(self.param_name)
        return res

    def __set__(self, instance, value):
        with instance.property_lock:
            config_dict = instance._get_config_dict(instance.path)
            old_config_dict = config_dict.copy()

            config_dict[self.param_name] = value
            with open(instance.path, 'w') as config_file:
                try:
                    json.dump(config_dict, config_file)
                    instance._ready_to_print = value
                except:
                    json.dump(old_config_dict, config_file)


class Client:
    """
    Singleton-класс.
    """
    property_lock = None
    _instance = None

    ready_to_print = ConfigProperty('ready_to_print')
    num_of_pages_in_tray = ConfigProperty('num_of_pages_in_tray')
    num_of_pages_of_cartridge = ConfigProperty('num_of_pages_of_cartridge')
    num_of_pages_of_color_cartridge = ConfigProperty('num_of_pages_of_color_cartridge')

    def __init__(self, path, property_lock, client_logger):
        self.client_logger = client_logger
        self.path = path
        # объект лок нужен для контроля read/write операций над свойствами
        self.property_lock = property_lock
        config_dict = self._get_config_dict(self.path)
        self.secret_key = config_dict.get('secret_key')
        self.name_of_good_printer = config_dict.get('name_of_good_printer')
        self.name_of_defective_printer = config_dict.get('name_of_defective_printer')
        self.main_url = config_dict.get('main_url')
        self.printer_id = config_dict.get('printer_id')
        self.monochrome_printing_mode = config_dict.get('monochrome_printing_mode')
        self.color_printing_mode = config_dict.get('color_printing_mode')
        self.no_flip_mode = config_dict.get('no_flip_mode')
        self.flip_up_mode = config_dict.get('flip_up_mode')
        self.flip_over_mode = config_dict.get('flip_over_mode')
        self.printer_warm_up_time = config_dict.get('printer_warm_up_time')
        self.one_page_print_time = config_dict.get('one_page_print_time')

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_config_dict(self, path):
        # можно использовать только в лочных операциях - внутри дескриптора
        # данный метод используется только в потокобезопасных операциях, поэтому его лочить не надо
        with open(path, 'r') as config_file:
            config_dict = json.load(config_file)

        return config_dict

    def send_info_about_good_job(self, task_id):
        """
        Отправляет POST запрос, чтобы сообщить серверу, что задача была успешно выполнена.
        :param task_id:
        :return: - (status, type_of_status)
        """
        data = {
            'printer_id': self.printer_id,
            'secret_key': self.secret_key,
            'task_id': task_id,
        }
        response = requests.post(f'{self.main_url}/printer_api/task/successfully_printed', json=data,
                                 headers={"Content-Type": "application/json"})

        if response.headers.get('Content-Type') == 'application/json':
            data = response.json()
            status = data['status']
            type_of_status = data['type']
            if status == 'error':
                if type_of_status == 'not_all_properties_had_sent':
                    return ('error', type_of_status)
                elif type_of_status == 'invalid_printer':
                    return ('error', type_of_status)
                elif type_of_status == 'task_doesnt_exist':
                    return ('error', type_of_status)
                elif type_of_status == 'error_of_task_current_status':
                    return ('error', type_of_status)
                elif type_of_status == 'not_json_data_had_sent':
                    return ('error', type_of_status)
            elif status == 'ok':
                if type_of_status == 'changes_applied':
                    return ('ok', type_of_status)
        else:
            return 'error', 'unexpected_server_response'

    def send_info_about_error(self, task_id, error_text):
        """
        Сообщает серверу о том, что при печати произошла ошибка.
        :param task_id:
        :param error_text:
        :return: status, type_of_status
        """
        data = {
            'printer_id': self.printer_id,
            'secret_key': self.secret_key,
            'task_id': task_id,
            'error_text': error_text,
        }
        response = requests.post(f'{self.main_url}/printer_api/task/error', json=data,
                                 headers={"Content-Type": "application/json"})

        if response.headers.get('Content-Type') == 'application/json':
            data = response.json()
            status = data['status']
            type_of_status = data['type']
            if status == 'error':
                if type_of_status == 'not_all_properties_had_sent':
                    return 'error', type_of_status
                elif type_of_status == 'invalid_printer':
                    return 'error', type_of_status
                elif type_of_status == 'task_doesnt_exist':
                    return 'error', type_of_status
                elif type_of_status == 'error_of_task_current_status':
                    return 'error', type_of_status
                elif type_of_status == 'not_json_data_had_sent':
                    return 'error', type_of_status
            elif status == 'ok':
                return 'ok', type_of_status
        else:
            return 'error', 'unexpected_server_response'

    def get_task_for_printing(self, consumer_interacts_with_shared_objects_event, producer_interacts_with_shared_objects_event):
        data = {
            'printer_id': self.printer_id,
            'secret_key': self.secret_key,
            'ready_to_print': self.ready_to_print,
            'num_of_pages_in_tray': self.num_of_pages_in_tray,
            'num_of_pages_of_cartridge': self.num_of_pages_of_cartridge,
            'num_of_pages_of_color_cartridge': self.num_of_pages_of_color_cartridge
        }

        # перед вызовом разрешаем consumer'у использовать общие объекты, т.к. лонг пулл запрос долгий и будет блочить
        consumer_interacts_with_shared_objects_event.set()

        response = requests.post(f'{self.main_url}/printer_api/task/get_task_for_printing', json=data,
                                 headers={"Content-Type": "application/json"})

        # закрываем доступ consumer'у к общим объектам
        consumer_interacts_with_shared_objects_event.clear()
        # дожидаемся, пока consumer закончит свою работу и даст поработать producer'у
        producer_interacts_with_shared_objects_event.wait()

        if response.headers.get('Content-Type') in [r'application/x-zip-compressed', r'application/zip']:
            dirname = response.headers.get('Content-Disposition').split('filename=')[-1].split('.')[0]

            dir_path = f'./print_docs/user_tasks'
            task_path = f'{dir_path}/{dirname}'

            # если папка задачи уже есть, то мы ее удаляем
            if dirname in os.listdir(dir_path):
                shutil.rmtree(task_path)

            os.mkdir(task_path)
            with zipfile.ZipFile(io.BytesIO(response.content)) as zfile:
                zfile.extractall(task_path)

            # ждем пока сохранится файл
            task = self._check_loaded_files(task_path, 180)
            if task:
                return 'task_received', task
            else:
                return 'error', 'files_from_response_not_saved'

        elif response.headers.get('Content-Type') == 'application/json':
            data = response.json()
            status = data['status']
            type_of_status = data['type']
            if status == 'error':
                if type_of_status == 'not_all_properties_had_sent':
                    return ('error', type_of_status)
                elif type_of_status == 'invalid_printer':
                    return ('error', type_of_status)
                elif type_of_status == 'not_all_user_files_had_uploaded':
                    return ('error', type_of_status)
                elif type_of_status == 'not_all_properties_had_sent':
                    return ('error', type_of_status)
                elif type_of_status == 'not_json_data_had_sent':
                    return ('error', type_of_status)
            elif status == 'ok':
                if type_of_status == 'not_found_new_tasks_for_printer':
                    return ('ok', type_of_status)
                # условие для того, чтобы дать команду с сервера о том, что принтер не может печатать
                elif type_of_status == 'printer_is_not_ready_to_print':
                    return ('ok', type_of_status)
        else:
            self.client_logger.error(f"Клиент получил от сервера сообщение с заголовком Content-Type: {response.headers.get('Content-Type')}, response: {response}, response content: {response.content}")
            return 'error', 'unexpected_server_response'

    def _check_loaded_files(self, task_path, time_to_save):
        start_time = time.time()
        while True:
            current_time = time.time()
            if current_time > start_time + time_to_save:
                break
            if os.path.isdir(task_path):
                all_filenames_in_task_dir = os.listdir(task_path)
                if 'properties.json' in all_filenames_in_task_dir:
                    task = Task(task_path)
                    all_filenames_in_task_dir = os.listdir(task_path)
                    necessary_filenames = task.filenames
                    if len(necessary_filenames) == len(
                            list(filter(lambda filename: filename in all_filenames_in_task_dir, necessary_filenames))):
                        self.client_logger.info(f'Документы task - {task.task_id} были успешно сохранены по адресу {task_path}')
                        return task
        return False

if __name__ == '__main__':
    client = Client('config.json', threading.Lock())
    """
    while True:
        status, type_of_status = client.get_task_for_printing()
        if status == 'ok':
            break
    """
    # print(client.get_task_for_printing())
    # print(client.send_info_about_error(1, 'error', ))








