import json
from io import BytesIO


def get_msg_for_dispatch_of_files(printer_id, secret_key, task_id, num_of_pages_of_task, color_mode,
                                  flip_mode, num_of_copies, filenames):
    data = {'printer_id': printer_id, 'secret_key': secret_key, 'task_id': task_id,
         'num_of_pages_of_task': num_of_pages_of_task, 'color_mode': color_mode, 'flip_mode': flip_mode,
         'num_of_copies': num_of_copies, 'filenames': filenames}
    stream = BytesIO()
    stream.write(json.dumps(data).encode())
    stream.seek(0)
    return stream














