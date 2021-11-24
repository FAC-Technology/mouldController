import datetime as dt
import time
# import os
import matplotlib
import matplotlib.animation as animation

from pages import defaults
from pages.mouldMonitor import MouldMonitor


t0 = time.time()
#
# log = logging.getLogger()
# console = logging.StreamHandler()
# format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
# console.setFormatter(logging.Formatter(format_str))
# handler = logging.handlers.WatchedFileHandler(
#     os.environ.get("LOGFILE", "logs/main.log"))
# handler.setFormatter(logging.Formatter(format_str))
# log.addHandler(handler)
# log.setLevel(os.environ.get("LOGLEVEL", "INFO"))
matplotlib.use("TkAgg")


app = MouldMonitor(ip_file=defaults.IP_FILE)
ani = animation.FuncAnimation(app.f, app.animate, interval=1000)

# log.info('Starting running')
while app.is_running():
    app.update_idletasks()
    app.update()
    if (dt.datetime.now() - app.ip_check_time).total_seconds() > defaults.IP_CHECK_PERIOD * 60:
        app.update_ip_list()
