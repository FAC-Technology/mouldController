import logging
from logging import handlers
import os

LOG_FOLDER = "mould logs"
EXPORT_FOLDER = 'Mould Temperature Exports'
LOGO_FILE = "FACT_LOGO.png"
GRAPH_EXPORT_NAME = "TemperatureReport_{}-{}"
EXPORT_PATH = os.path.expanduser(os.path.join('~', 'Documents', EXPORT_FOLDER))
IP_FILE = os.path.expanduser(os.path.join('~','Desktop',"IP_ADDRESSES.txt"))
IP_CHECK_PERIOD = 0.05  # minutes
DATE_FORMAT = "%d-%m-%y"
TIME_FORMAT = "%H:%M:%S"
FNAME_TIME_FORMAT = "%H-%M-%S"
DATETIME_FORMAT = DATE_FORMAT + '_' + TIME_FORMAT
lineStyles = ("rx", "gx", "bx", "ro", "go", "bo", "rd", "gd", "bd")
LARGE_FONT = ("Arial", 14)
SMALL_FONT = ("Arial", 12)
LOG_FILE_NAMING = "Temperature Log {} {}.csv"

# check prerequisite files exist.
# exists in /Documents/Mould Temperature Exports
if not os.path.isdir(EXPORT_PATH):
    os.mkdir(EXPORT_PATH)

if not os.path.isdir(LOG_FOLDER):
    os.mkdir(LOG_FOLDER)
    with open(os.path.join(LOG_FOLDER, "main.log"),'w+'):
        pass

if not os.path.isfile(IP_FILE):
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

LOREM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et 
dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo 
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. """