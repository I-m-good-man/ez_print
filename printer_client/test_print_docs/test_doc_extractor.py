import os
import zipfile
import xml.dom.minidom
import PyPDF2


class NotFoundPagesProperty(Exception):
    ...

class UndefinedNumOfPages(Exception):
    ...

class UndefinedTypeOfNumOfPages(Exception):
    ...


def get_number_of_docx_document_pages(file):
    """
    Функция для вывода количества страниц docx, docm, dotx, dotm -документов.
    :param file: file-object или путь до файла
    :return:
    """
    document = zipfile.ZipFile(file)
    if 'docProps/app.xml' in document.namelist():
        props = document.read('docProps/app.xml')
        dom = xml.dom.minidom.parseString(props)
        list_of_values = dom.getElementsByTagName("Pages")
        if len(list_of_values) == 1:
            num_of_pages = list_of_values[0].firstChild.nodeValue
            try:
                num_of_pages = int(num_of_pages)
                return num_of_pages
            except:
                raise UndefinedTypeOfNumOfPages(f'В файле {file} количество страниц имеет тип {type(num_of_pages)}')
        else:
            raise UndefinedNumOfPages(f'В файле {file} было найдено {len(list_of_values)} тегов pages.')
    else:
        raise NotFoundPagesProperty(f'Не нашли у документа {file} поле docProps/app.xml!')


def get_number_of_odt_document_pages(file):
    """
    Функция для вывода количества страниц odt-документа.
    :param file: file-object или путь до файла
    :return:
    """
    document = zipfile.ZipFile(file)
    if 'meta.xml' in document.namelist():
        props = document.read('meta.xml')
        dom = xml.dom.minidom.parseString(props)
        list_of_values = dom.getElementsByTagName("meta:document-statistic")
        if len(list_of_values) == 1:
            num_of_pages = list_of_values[0].getAttribute('meta:page-count')
            try:
                num_of_pages = int(num_of_pages)
                return num_of_pages
            except:
                raise UndefinedTypeOfNumOfPages(f'В файле {file} количество страниц имеет тип {type(num_of_pages)}')
        else:
            raise UndefinedNumOfPages(f'В файле {file} было найдено {len(list_of_values)} тегов pages.')
    else:
        raise NotFoundPagesProperty(f'Не нашли у документа {file} поле docProps/app.xml!')


def get_number_of_pdf_document_pages(file):
    """
    Функция для вывода количества страниц pdf-документа.
    :param file: file-object
    :return:
    """
    read_pdf = PyPDF2.PdfFileReader(file)
    num_of_pages = read_pdf.numPages
    if isinstance(num_of_pages, int):
        return num_of_pages
    else:
        raise UndefinedTypeOfNumOfPages(f'В файле {file} количество страниц имеет тип {type(num_of_pages)}')


print(get_number_of_docx_document_pages('test_page_counter_docs/2.docx'))

with open(r'test_page_counter_docs/2.docx', 'rb') as file:
    get_number_of_docx_document_pages(file)



"""
Доступные форматы: docx, docm, dotx, dotm

"""

"""
У doc, txt, pdf  документа нет информации о страницах
"""

# print(get_number_of_docx_document_pages('./test_page_counter_docs/2.pdf'))


"""
for file in os.listdir('./test_page_counter_docs'):
    full_filename = f'./test_page_counter_docs/{file}'
    print(get_number_of_document_pages(full_filename))

"""

