import datetime as dt
import matplotlib
import matplotlib.animation as animation

from pages import defaults
from pages.mouldMonitor import MouldMonitor


matplotlib.use("TkAgg")

app = MouldMonitor(ip_file=defaults.IP_FILE)
ani = animation.FuncAnimation(app.f, app.animate, interval=1000)

defaults.log.info('Starting running')

while app.is_running():
    app.update_idletasks()
    app.update()
    if (dt.datetime.now() - app.ip_check_time).total_seconds() > defaults.IP_CHECK_PERIOD * 60:
        app.update_ip_list()
