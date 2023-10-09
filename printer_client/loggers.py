import logging
from logging.handlers import RotatingFileHandler

def get_client_logger():
    client_logger = logging.getLogger('client_logger')
    client_logger.setLevel(logging.INFO)
    client_logger_file_handler = RotatingFileHandler('client_logs.log', mode='a', maxBytes=10**9, backupCount=5)
    client_logger_file_handler.setLevel(logging.INFO)
    client_logger_stream_handler = logging.StreamHandler()
    client_logger_stream_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(threadName)s- %(lineno)d - %(message)s')
    client_logger_file_handler.setFormatter(file_format)
    client_logger_stream_handler.setFormatter(file_format)
    client_logger.addHandler(client_logger_file_handler)
    client_logger.addHandler(client_logger_stream_handler)

    return client_logger


def get_printer_logger():
    printer_logger = logging.getLogger('logger')
    printer_logger.setLevel(logging.INFO)
    printer_logger_file_handler = RotatingFileHandler('printer_logs.log', mode='a', maxBytes=10**9, backupCount=5)
    printer_logger_stream_handler = logging.StreamHandler()
    printer_logger_file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(threadName)s- %(lineno)d - %(message)s')
    printer_logger_file_handler.setFormatter(file_format)
    printer_logger_stream_handler.setFormatter(file_format)
    printer_logger.addHandler(printer_logger_file_handler)
    printer_logger.addHandler(printer_logger_stream_handler)
    return printer_logger

if __name__ == '__main__':
    client_logger = get_client_logger()
    client_logger.error("аа")
    # client_logger.error("бб")
    # client_logger.error("вв")









