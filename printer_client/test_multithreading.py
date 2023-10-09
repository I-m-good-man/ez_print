import threading
import time
import json
import concurrent.futures


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

            config_dict['ready_to_print'] = value
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

    def __init__(self, path, property_lock, method_lock):
        self.path = path
        # объект лок нужен для контроля read/write операций над свойствами
        self.property_lock = property_lock
        self.method_lock = method_lock
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

    def _method_lock_decorator(method):
        def inner(self, *args, **kwargs):
            with self.method_lock:
                res = method(self, *args, **kwargs)
            return res
        return inner

    @_method_lock_decorator
    def send_info_about_good_job(self, task_id):
        print(f'Start send_info_about_good_job {task_id}')
        time.sleep(10)
        print('send_info_about_good_job About to get ready_to_print')
        print(f'ready_to_print: {self.ready_to_print}')

        print(f'Finish send_info_about_good_job {task_id}')
        return task_id

    @_method_lock_decorator
    def send_info_about_error(self, task_id):
        print(f'Start send_info_about_error {task_id}')
        time.sleep(10)
        print('send_info_about_error About to get ready_to_print')
        print(f'ready_to_print: {self.ready_to_print}')
        print(f'Finish send_info_about_error {task_id}')
        return task_id


# class ProducerConsumer:
#         def __new__(cls, *args, **kwargs):
#             if cls._instance is None:
#                 cls._instance = super().__new__(cls)
#                 cls.task_pipeline = kwargs.get('task_pipeline')
#             return cls._instance


if __name__ == '__main__':
    client = Client(r'/printer_client/config.json', threading.Lock(),
                    threading.Lock())
    def f1():
        for i in range(2):
            print(client.send_info_about_good_job(i))

    def f2():
        time.sleep(2)
        for i in range(10, 12):
            print(client.send_info_about_error(i))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(f1)
        executor.submit(f2)


