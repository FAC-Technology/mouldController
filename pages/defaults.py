import logging
from logging import handlers
import os

LOG_FOLDER = "mould logs/"
EXPORT_FOLDER = 'Mould Temperature Exports'
EXPORT_PATH = os.path.expanduser(os.path.join('~', 'Documents', EXPORT_FOLDER))
IP_FILE = "IP_ADDRESSES.txt"
IP_CHECK_PERIOD = 0.05  # minutes
DATE_FORMAT = "%d-%m-%y"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = DATE_FORMAT + '_' + TIME_FORMAT
lineStyles = ("rx", "gx", "bx", "ro", "go", "bo", "rd", "gd", "bd")
LARGE_FONT = ("Arial", 14)
SMALL_FONT = ("Arial", 12)
LOG_FILE_NAMING = "Temperature Log {} {}.csv"
log = logging.getLogger()
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "logs/main.log"))
handler.setFormatter(logging.Formatter(format_str))
log.addHandler(handler)
log.setLevel(os.environ.get("LOGLEVEL", "INFO"))
