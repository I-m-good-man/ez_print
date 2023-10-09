from io import BytesIO
from zipfile import ZipFile
import os
import json


class NotAllFilesExist(Exception):
    ...


def get_archive_of_files(filenames, json_properties):
    existed_filenames = os.listdir('./files_for_print/')
    # existed_filenames = os.listdir('../files_for_print/')
    # если все файлы из filenames есть в existed_filenames, то можно отправлять файлы
    if list(filter(lambda x: x in existed_filenames, filenames)) == filenames:
        stream = BytesIO()
        with ZipFile(stream, 'w') as zf:
            for filename in filenames:
                zf.write(f'./files_for_print/{filename}', filename)
                # zf.write(f'../files_for_print/{filename}', filename)
            zf.writestr('properties.json', json_properties.getbuffer())
        stream.seek(0)
        return stream
    else:
        raise NotAllFilesExist(f'Файлы {list(filter(lambda x: x not in existed_filenames, filenames))} не сущестуют!')


def delete_files(filenames):
    existed_filenames = os.listdir('./files_for_print/')
    if list(filter(lambda x: x in existed_filenames, filenames)) == filenames:
        for filename in filenames:
            file_path = f'./files_for_print/{filename}'
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        raise NotAllFilesExist(f'Файлы {list(filter(lambda x: x not in existed_filenames, filenames))} не сущестуют!')


if __name__ == '__main__':
    data = {'name': 'marat'}
    stream = BytesIO()
    stream.write(json.dumps(data).encode())
    stream.seek(0)
    stream = get_archive_of_files(['1_1.docx', '1_3.docx'], stream.getbuffer())
    with open('arc.zip', 'wb') as file:
        file.write(stream.getbuffer())