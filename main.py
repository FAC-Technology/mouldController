import datetime as dt
import matplotlib
import matplotlib.animation as animation

from pages import defaults
from pages.mouldMonitor import MouldMonitor
import os

matplotlib.use("TkAgg")

# make the destination for exports, if not existing already.
# exists in /Documents/Mould Temperature Exports

if not os.path.isdir(defaults.EXPORT_PATH):
    os.mkdir(defaults.EXPORT_PATH)

# initialise the class object holding the window.
app = MouldMonitor(ip_file=defaults.IP_FILE)
# every 1000ms, update the graph using the animate method
ani = animation.FuncAnimation(app.f, app.animate, interval=1000)
app.initialise_plots()  # initialise the plots with the existing data.
defaults.log.info('Starting running')

while app.is_running():
    # app.update_idletasks()
    app.update()
    if (dt.datetime.now() - app.ip_check_time).total_seconds() > defaults.IP_CHECK_PERIOD * 60:
        app.update_ip_list()
        app.initialise_plots()
