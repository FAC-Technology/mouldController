import logging
from logging import handlers
import os


EXPORT_FOLDER = 'Mould Temperature Exports'
LOGO_FILE = "FACT_LOGO.png"
GRAPH_EXPORT_NAME = "TemperatureReport_{}-{}"
DESKTOP_FOLDER = "Mould Monitor"
DESKTOP_PATH = os.path.expanduser(os.path.join('~', 'Desktop', DESKTOP_FOLDER))
LOG_FOLDER = "Data Logs"
IP_FILENAME = "IP_ADDRESSES.txt"
EXPORT_PATH = os.path.join(DESKTOP_PATH, EXPORT_FOLDER)
IP_FILE = os.path.join(DESKTOP_PATH, IP_FILENAME)
LOG_FOLDER = os.path.join(DESKTOP_PATH, LOG_FOLDER)
IP_CHECK_PERIOD = 0.25  # minutes
DATE_FORMAT = "%d-%m-%y"
TIME_FORMAT = "%H:%M:%S"
FNAME_TIME_FORMAT = "%H-%M-%S"
DATETIME_FORMAT = DATE_FORMAT + '_' + TIME_FORMAT
lineStyles = ("r", "g", "b", "r--", "g--", "b--", "r:", "g:", "b:")
LARGE_FONT = ("Arial", 14)
SMALL_FONT = ("Arial", 12)
LOG_FILE_NAMING = "Temperature Log {} {}.csv"

# check prerequisite files exist.
# exists in /Documents/Mould Temperature Exports
if not os.path.isdir(DESKTOP_PATH):  # check destination folder
    os.mkdir(DESKTOP_PATH)

if not os.path.isdir(EXPORT_PATH):  # check export folder
    os.mkdir(EXPORT_PATH)

if not os.path.isdir(LOG_FOLDER):  # check folder for longs
    os.mkdir(LOG_FOLDER)
    with open(os.path.join(LOG_FOLDER, "main.log"), 'w+'):  # touch main log file
        pass

if not os.path.isfile(IP_FILE):  # IP address folder
    with open(IP_FILE, 'w+') as f:
        f.writelines(["# IP address list for Eurotherm nanodacs\n",
                      "# Any line not of form X.X.X.X is ignored\n",
                      "x192.168.0.1\n"])

log = logging.getLogger()
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", f"{LOG_FOLDER}/main.log"))
handler.setFormatter(logging.Formatter(format_str))
log.addHandler(handler)
log.setLevel(os.environ.get("LOGLEVEL", "INFO"))
