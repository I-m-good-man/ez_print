import json
import os
import shutil
import time


class Task:
    def __init__(self, task_path):
        self.task_path = task_path
        self.path = os.path.join(task_path, 'properties.json')
        task_properties_dict = self.get_task_properties_dict(self.path)
        self.printer_id = task_properties_dict.get('printer_id')
        self.secret_key = task_properties_dict.get('secret_key')
        self.task_id = task_properties_dict.get('task_id')
        self.num_of_pages_of_task = task_properties_dict.get('num_of_pages_of_task')
        self.color_mode = task_properties_dict.get('color_mode')
        self.flip_mode = task_properties_dict.get('flip_mode')
        self.num_of_copies = task_properties_dict.get('num_of_copies')
        self.filenames = task_properties_dict.get('filenames')

        if task_properties_dict.get('removal_time') is None:
            # self.removal_time = self.add_removal_time(3*24*60*60)
            self.removal_time = self.add_removal_time(60)

        else:
            self.removal_time = task_properties_dict.get('removal_time')

    @property
    def epoch_time(self):
        return int(time.time())

    @staticmethod
    def get_task_properties_dict(path):
        with open(path, 'r') as task_properties_file:
            config_dict = json.load(task_properties_file)
        return config_dict

    def delete_task_dir(self):
        # удаляем папку с таском
        if os.path.isdir(self.task_path):
            shutil.rmtree(self.task_path)

    def add_removal_time(self, time_to_live):
        removal_time = int(self.epoch_time + time_to_live)

        config_dict = self.get_task_properties_dict(self.path)
        config_dict['removal_time'] = removal_time
        with open(self.path, 'w') as task_properties_file:
            json.dump(config_dict, task_properties_file)
        return removal_time



if __name__ == '__main__':
    task = Task(r'C:\Users\marat\PycharmProjects\learn_web\EasyPrint_MAIN\printer_client\print_docs\user_tasks\1')









