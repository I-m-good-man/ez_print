import zipfile
import xml.dom.minidom
import PyPDF2


class UndefinedTypeOfFile(Exception):
    ...

class NotFoundPagesProperty(Exception):
    ...

class UndefinedNumOfPages(Exception):
    ...

class UndefinedTypeOfNumOfPages(Exception):
    ...


class CounterPages:
    @staticmethod
    def get_number_of_xml_structured_document_pages(file):
        """
        Функция для вывода количества страниц docx, docm, dotx, dotm -документов.
        :param file: file-object или путь до файла
        :return:
        """
        try:
            document = zipfile.ZipFile(file)
        except zipfile.BadZipFile:
            raise UndefinedTypeOfFile(f'Из файла {file} нельзя извлечь информацию о количестве страниц!')
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

    @staticmethod
    def get_number_of_odt_document_pages(file):
        """
        Функция для вывода количества страниц odt-документа.
        :param file: file-object или путь до файла
        :return:
        """
        try:
            document = zipfile.ZipFile(file)
        except zipfile.BadZipFile:
            raise UndefinedTypeOfFile(f'Из файла {file} нельзя извлечь информацию о количестве страниц!')
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

    @staticmethod
    def get_number_of_pdf_document_pages(file):
        """
        Функция для вывода количества страниц pdf-документа.
        :param file: file-object
        :return:
        """
        try:
            read_pdf = PyPDF2.PdfFileReader(file)
        except:
            raise UndefinedTypeOfFile(f'Ошибка при чтении pdf-файла {file}')
        num_of_pages = read_pdf.numPages
        if isinstance(num_of_pages, int):
            return num_of_pages
        else:
            raise UndefinedTypeOfNumOfPages(f'В файле {file} количество страниц имеет тип {type(num_of_pages)}')


def get_num_of_pages_of_document(file, filename):
    counter = CounterPages()
    extension_of_file = filename.split('.')[-1]
    if extension_of_file == 'pdf':
        return counter.get_number_of_pdf_document_pages(file)
    elif extension_of_file == 'odt':
        return counter.get_number_of_odt_document_pages(file)
    elif extension_of_file in ['docx', 'docm', 'dotx', 'dotm']:
        return counter.get_number_of_xml_structured_document_pages(file)



