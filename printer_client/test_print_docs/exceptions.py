class PrinterError(Exception):
    ...


class DeleteAllTasksError(PrinterError):
    ...


class PrintingError(PrinterError):
    ...


class DeleteJobError(PrinterError):
    ...


class JobNotFoundError(PrinterError):
    ...


class PagesNotFound(PrinterError):
    ...







