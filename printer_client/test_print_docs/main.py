import os
import time

import win32print
import win32api
from exceptions import *


#print_pdf (входной pdf, режим печати, какой принтер)
#режим печати: 1 - односторонняя, 2 двойная по длинному краю, 3 - по короткому
def print_pdf(input_pdf, mode=2):
    name = 'Hewlett-Packard hp LaserJet 2300 series'
    try:
        # Устанавливаем дефолтный принтер
        win32print.SetDefaultPrinterW(name)
        win32print.SetDefaultPrinter(name)
    finally:
        # Если не получилось или получилось -&gt; устанавливаем этот принтер стандартом
        name = win32print.GetDefaultPrinter()

    # оставляем без изменений
    ## тут нужные права на использование принтеров
    printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
    ## начинаем работу с принтером ("открываем" его)
    handle = win32print.OpenPrinter(name, printdefaults)
    ## Если изменить level на другое число, то не сработает
    level = 2
    ## Получаем значения принтера
    attributes = win32print.GetPrinter(handle, level)
    ## Настройка двухсторонней печати
    attributes['pDevMode'].Duplex = mode   #flip over  3 - это короткий 2 - это длинный край

    ## Передаем нужные значения в принтер
    win32print.SetPrinter(handle, level, attributes, 0)
    win32print.GetPrinter(handle, level)['pDevMode'].Duplex
    ## Предупреждаем принтер о старте печати
    win32print.StartDocPrinter(handle, 1, [input_pdf, None, "raw"])
    ## 2 в начале для открытия pdf и его сворачивания, для открытия без сворачивания поменяйте на 1
    win32api.ShellExecute(2, 'print', input_pdf, '.', '/manualstoprint', 0)
    ## "Закрываем" принтер
    win32print.ClosePrinter(handle)

path_file = r'C:\Users\marat\PycharmProjects\learn_web\learn_flask\EasyPrint\printer_tests\docs\1.docx'
# path_file =
# print_pdf(path_file, mode=3)
"""
# Пример
inputs_print = next(os.walk(outdir))[2] # Берем все файлы в папке outdir
# Печатаем документы
for input_print in inputs_print:
    # Путь до файла, который нужно расспечатать
    path_print = outdir + input_print
    # Если в названии файла есть 'Экзаменационный', то печатаем по короткому краю
    if 'Экзаменационный' in input_print:
        print_pdf(path_print, 3, num)
    else:
        print_pdf(path_print, 2, num)

"""



def print2():
    import win32api
    import win32print

    name = win32print.GetDefaultPrinter()

    #printdefaults = {"DesiredAccess": win32print.PRINTER_ACCESS_ADMINISTER}
    printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
    handle = win32print.OpenPrinter(name, printdefaults)

    level = 2
    attributes = win32print.GetPrinter(handle, level)


    #attributes['pDevMode'].Duplex = 1    # no flip
    attributes['pDevMode'].Duplex = 2    # flip up
    # attributes['pDevMode'].Duplex = 3    # flip over

    ## 'SetPrinter' fails because of 'Access is denied.'
    ## But the attribute 'Duplex' is set correctly
    try:
        win32print.SetPrinter(handle, level, attributes, 0)
    except:
        print("win32print.SetPrinter: set 'Duplex'")

    res = win32api.ShellExecute(0, 'print', r'.\docs\1.docx', None, '.', 0)
    time.sleep(5)

    win32print.ClosePrinter(handle)


def autoprint(file_name):
    import win32print
    name = win32print.GetDefaultPrinter()
    printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
    handle = win32print.OpenPrinter(name, printdefaults)
    level = 2
    attributes = win32print.GetPrinter(handle, level)   # http://timgolden.me.uk/pywin32-docs/PyDEVMODE.html
                                   # All are int() variables
    attributes['pDevMode'].Duplex = 1    # no flip
    # attributes['pDevMode'].Duplex = 2    # flip up - перевернуть по короткой стороне, т.е. от себя сверху вниз перевернуть
    # attributes['pDevMode'].Duplex = 3    # flip over - перевернуть по длинной стороне, т.е. перевернуть как в книгу страницы - это лучше

    attributes['pDevMode'].Copies = 1    # Num of copies

    #attributes['pDevMode'].Color = 1    # Color
    attributes['pDevMode'].Color = 2    # Monochrome

    attributes['pDevMode'].Collate = 1    # Collate TRUE
    #attributes['pDevMode'].Collate = 2    # Collate FALSE

    try:
        win32print.SetPrinter(handle, level, attributes, 0)
    except:
        print("win32print.SetPrinter: settings could not be changed")

    try:

        res = win32api.ShellExecute(0, 'print', file_name, None, '.', 0)
        time.sleep(1)

        print("Printing now...")
        win32print.ClosePrinter(handle)

    except Exception as e:
        print(str(e))
        print("--Failed to print--")
        time.sleep(5)



def print_job_checker():
    """
    Prints out all jobs in the print queue every 5 seconds
    """
    jobs = [1]
    while jobs:
        jobs = []
        for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,
                                         None, 1):
            flags, desc, name, comment = p

            phandle = win32print.OpenPrinter(name)
            print_jobs = win32print.EnumJobs(phandle, 0, -1, 1)
            if print_jobs:
                jobs.extend(list(print_jobs))
            for job in print_jobs:
                print("printer name => ", name)
                document = job["pDocument"]
                print("Document name => ", document)
            win32print.ClosePrinter(phandle)

    print("No more jobs!")


def print_job_deleter():
    """
    Prints out all jobs in the print queue every 5 seconds
    """
    jobs = [1]
    while jobs:
        jobs = []
        for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,
                                         None, 1):
            flags, desc, name, comment = p

            phandle = win32print.OpenPrinter(name)

            print_jobs = win32print.EnumJobs(phandle, 0, -1, 1)

            if print_jobs:
                jobs.extend(list(print_jobs))

            for job in print_jobs:

                print(job['TotalPages'])

                if(job['TotalPages'] >= 1):
                    print(type(job))
                    win32print.SetJob(phandle, job['JobId'], 0, None, win32print.JOB_CONTROL_DELETE)

            win32print.ClosePrinter(phandle)

        time.sleep(0.25)
    print("No more jobs!")



import time

#constants

wp = win32print

# lists and dicitonaries of constants
ptypelist =[(wp.PRINTER_ENUM_SHARED,'shared'),(wp.PRINTER_ENUM_LOCAL,'local'),(wp.PRINTER_ENUM_CONNECTIONS,'network')]

cmds = {'Pause': wp.JOB_CONTROL_PAUSE, 'cancel': wp.JOB_CONTROL_CANCEL, 'resume': wp.JOB_CONTROL_RESUME,
'prior_low': wp.MIN_PRIORITY, 'prior_high': wp.MAX_PRIORITY, 'prior_normal': wp.DEF_PRIORITY
}
statuscodes ={'deleting':wp.JOB_STATUS_DELETING,'error':wp.JOB_STATUS_ERROR,'offline':wp.JOB_STATUS_OFFLINE,
              'paper out':wp.JOB_STATUS_PAPEROUT,'paused':wp.JOB_STATUS_PAUSED,'printed':wp.JOB_STATUS_PRINTED,
              'printing':wp.JOB_STATUS_PRINTING,'spooling':wp.JOB_STATUS_SPOOLING}


class PMFuncs:
    def __init__(self, good_printer_name, defective_printer_name):
        # initialise the list of printers
        self.PList = []
        self.good_printer_name = good_printer_name
        self.defective_printer_name = defective_printer_name

    def get_default_printer(self):
        DefPName = win32print.GetDefaultPrinter()
        return DefPName

    def set_default_printer(self, name):
        win32print.SetDefaultPrinterW(name)
        win32print.SetDefaultPrinter(name)

    def get_printer_list(self):
        # returns a list of dicts.
        # this gets the default printer
        tmpdic ={}
        DefPName = win32print.GetDefaultPrinter()

        # Get the default printer firstso we can add this to the list of printers

        for pt in ptypelist:
         try:
             for (Flags, pDescription, pName, pComment) in list(win32print.EnumPrinters(pt[0], None, 1)):
                 tmpdic ={}
                 tmpdic['PType'] = pt[1]
                 tmpdic['Flags'] = Flags
                 tmpdic['Description'] = pDescription
                 #test for if this is the default printer
                 if pName == DefPName:
                     tmpdic['DefPrinter':True]
                 else:
                     tmpdic['DefPrinter':False]
                 tmpdic['Name'] = pName
                 tmpdic['Comment'] = pComment
                 print(tmpdic)
                 self.PList.append(tmpdic)
         except:
             pass    #no printers of this type so don't add anything

        return self.PList   #list of installed printers

    def get_job_list(self, printer):
        phandle = win32print.OpenPrinter(printer)
        #now get all the print jobs (start at job 0 and -1 for all jobs)
        jlist = win32print.EnumJobs(phandle,0,-1,1)
        win32print.ClosePrinter(phandle)
        return jlist    # this lists all jobs on all printers

    def get_job_info(self, printer, jobID):
        phandle = win32print.OpenPrinter(printer)
        ilist = win32print.GetJob(phandle, jobID, 1)
        win32print.ClosePrinter(phandle)
        return ilist    #this lists all info available at level 1 for selected job.

    def set_job_cmd(self, printer, jobID, JobInfo, RCmd):
        phandle = win32print.OpenPrinter(printer)
        win32print.SetJob(phandle, jobID, 1, JobInfo, Cmds[RCmd])
        win32print.ClosePrinter(phandle)

    def delete_job(self, printer, job_id):
        phandle = win32print.OpenPrinter(printer)

        print_jobs = win32print.EnumJobs(phandle, 0, -1, 1)

        job_is_deleted = False
        for job in print_jobs:
            if job['JobId'] == job_id:
                win32print.SetJob(phandle, job['JobId'], 0, None, win32print.JOB_CONTROL_DELETE)
                job_is_deleted = True
                break
        win32print.ClosePrinter(phandle)

        if job_is_deleted:
            return True
        else:
            raise DeleteJobError(f'Работа с job_id {job_id} на принтере {printer} не была удалена!')

    def delete_all_jobs(self, printer, time_of_waiting_to_delete=60):
        phandle = win32print.OpenPrinter(printer)

        all_jobs_have_deleted = False
        t0 = time.time()
        while time.time() - t0 < time_of_waiting_to_delete:
            print_jobs = win32print.EnumJobs(phandle, 0, -1, 1)
            if print_jobs:
                for job in print_jobs:
                    win32print.SetJob(phandle, job['JobId'], 0, None, win32print.JOB_CONTROL_DELETE)
            else:
                all_jobs_have_deleted = True
                break
        win32print.ClosePrinter(phandle)

        if all_jobs_have_deleted:
            return True
        else:
            raise DeleteAllTasksError(f'Не все задачи были удалены на принтере {printer}!')

    def print_file(self, printer, abs_path_to_file_directory, filename, color_mode=2, flip_mode=1, num_of_copies=1, collate=1):
        """
        Func for printing file.
        :param printer: printer name
        :param color_mode: 1-color, 2-monochrome
        :param filename:
        :param flip_mode: 1-no flip, 2-flip up, 3-flip over
        :param num_of_copies:
        :param collate: 1 - collate True, 2 - collate False
        :param time_of_waiting_of_print: - время, которое нужно на ожидание печати принтера
        :return:
        """

        printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
        try:
            handle = win32print.OpenPrinter(printer, printdefaults)
        except Exception as e:
            return str(e)

        level = 2
        try:
            attributes = win32print.GetPrinter(handle, level)
        except Exception as e:
            return str(e)

        attributes['pDevMode'].Duplex = flip_mode
        attributes['pDevMode'].Copies = num_of_copies
        attributes['pDevMode'].Color = color_mode
        attributes['pDevMode'].Collate = collate

        try:
            win32print.SetPrinter(handle, level, attributes, 0)
        except Exception as e:
            return str(e)

        # сначала опустошаем список задач, у нас в списке задач может быть не больше одной задачи всегда
        self.delete_all_jobs(printer)

        # res = win32api.ShellExecute(0, 'print', filename, None, '.', 0)
        res = win32api.ShellExecute(0, 'print', filename, None, abs_path_to_file_directory, 0)
        win32print.ClosePrinter(handle)

    def check_job_list_for_empty(self, printer, filename, time_of_waiting_of_print=60):
        # если спустя время time_of_waiting_of_print, в список задач принтера будет не пустым, то значит этот файл
        # не напечатался, ждем время time_of_waiting_of_print, чтобы список задач стал пустым
        printer_printed_file = False
        time_1 = time.time()
        while time.time() - time_1 < time_of_waiting_of_print:
            job_list = self.get_job_list(printer)
            if not job_list:
                printer_printed_file = True
                break

        if printer_printed_file:
            return True
        else:
            raise PrintingError(f'Принтер {printer}не распечатал файл {filename}!')

    def get_number_of_pages_of_job(self, printer, job_id):
        phandle = win32print.OpenPrinter(printer)

        print_jobs = win32print.EnumJobs(phandle, 0, -1, 1)
        num_of_pages = None
        for job in print_jobs:
            if job['JobId'] == job_id:
                num_of_pages = job.get('TotalPages')
                break

        win32print.ClosePrinter(phandle)
        return num_of_pages

    def get_num_of_pages_of_document(self, filename, time_to_wait_of_adding_to_job_list=60, **print_file_kwargs):
        """
        Чтобы узнать количество страниц, которое потребуется для печати документа, нужно:
        1) Отправлять задачи только на нерабочий принтер.
        2) Очистить список задач для печати
        3) Отправить на него печататься документ
        4) Мониторить список задач, пока там не появится отправленная нами единственная задача
        5) Узнать количество страниц этой задачи.
        6) Очистить список задач для печати
        7) Установить рабочий принтер как дефолтный обратно
        :return:
        """
        self.delete_all_jobs(self.defective_printer_name)
        self.print_file(self.defective_printer_name, filename, **print_file_kwargs)

        # ждем 10 секуннд, чтобы система успела отправить задачу печати
        time.wait(10)

        num_of_pages = 'Задача не найдена!'
        time_1 = time.time()
        while time.time() - time_1 < time_to_wait_of_adding_to_job_list:
            job_list = self.get_job_list(self.get_default_printer())
            if job_list:
                job = job_list[0]
                num_of_pages = job.get('TotalPages')
                break

        self.delete_all_jobs(self.defective_printer_name)
        
        if num_of_pages == 'Задача не найдена!':
            raise JobNotFoundError(f'Задача для файла "{filename}" была не найдена в очереди задач принтера!')
        elif num_of_pages is None:
            raise PagesNotFound(f'Нет информации о количестве страниц файла "{filename}"!')
        else:
            return num_of_pages


def main():
    p = PMFuncs('Hewlett-Packard hp LaserJet 2300 series', 'Samsung CLX-3300 Series')
    task_id = 1

    abs_path_to_user_files_dir = rf'{os.getcwd()}\user_tasks'
    abs_path_to_task_dir = fr'{abs_path_to_user_files_dir}\{task_id}'
    filename = '1_1.docx'
    print(abs_path_to_task_dir)
    print(p.print_file(p.defective_printer_name, abs_path_to_task_dir, filename))



if __name__ == "__main__":
    print(statuscodes)
