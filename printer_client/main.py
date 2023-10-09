import threading
import concurrent.futures
import time

from client_utils import Client, requests
from print_docs.printer_utils import PMFuncs
import loggers
from producer_consumer import ProducerConsumer, CheckableQueue


def close_program(client_logger, program_close_event, producer_is_closed_event, consumer_is_closed_event):
    while True:
        answer = input('Введите q, чтобы закрыть программу:')
        if answer.strip() == 'q':
            program_close_event.set()
            client_logger.info('Программа начала свое закрытие; идет ожидание завершения потоков producer и consumer')
            producer_is_closed_event.wait()
            consumer_is_closed_event.wait()
            client_logger.info('Потоки producer и consumer завершили свою работу\nПрограмма завершена!')
            time.sleep(10)
            break


if __name__ == '__main__':
    client_logger = loggers.get_client_logger()
    printer_logger = loggers.get_printer_logger()

    client = Client('config.json', threading.Lock(), client_logger)
    printer = PMFuncs(client.name_of_good_printer, client.name_of_defective_printer, printer_logger)
    task_pipeline = CheckableQueue()

    program_close_event = threading.Event()
    producer_is_closed_event = threading.Event()
    consumer_is_closed_event = threading.Event()

    producer_consumer_instance = ProducerConsumer(task_pipeline=task_pipeline, program_close_event=program_close_event,
                                                  producer_is_closed_event=producer_is_closed_event,
                                                  consumer_is_closed_event=consumer_is_closed_event)
    # while True:
    #     producer_consumer_instance._delete_old_tasks()

    # producer_consumer_instance.test_add_many_tasks()
    # producer_consumer_instance.consumer(printer, client, client_logger)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(producer_consumer_instance.producer, client, client_logger)
        executor.submit(producer_consumer_instance.consumer, printer, client, client_logger)
        executor.submit(close_program, client_logger, program_close_event, producer_is_closed_event,
                        consumer_is_closed_event)




