import datetime as dt
import time
import os
import matplotlib
import matplotlib.animation as animation
from matplotlib import style
import logging
import logging.handlers

from pages.mouldMonitor import MouldMonitor

LOG_FOLDER = "mould logs/"
IP_FILE = "IP_ADDRESSES.txt"
IP_CHECK_PERIOD = 0.05 # minutes
DATE_FORMAT = "%d-%m-%y"
TIME_FORMAT = "%H:%M:%S"
style.use("ggplot")
lineStyles = ("r--", "g--", "b--", "r:", "g:", "b:", "r-.", "g-.", "b-.")

t0 = time.time()

log = logging.getLogger()
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "logs/main.log"))
handler.setFormatter(logging.Formatter(format_str))
log.addHandler(handler)
log.setLevel(os.environ.get("LOGLEVEL", "INFO"))
matplotlib.use("TkAgg")


app = MouldMonitor(ip_file=IP_FILE)
ani = animation.FuncAnimation(app.f, app.animate, interval=1000)

log.info('Starting running')
ip_check_time = dt.datetime.now() - dt.timedelta(days=1) # initialise as last checking yesterday
app.old_IP_LIST = []
while app.is_running():
    app.update_idletasks()
    app.update()
    app.update_ip_list()
