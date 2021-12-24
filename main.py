import datetime as dt
import matplotlib
import matplotlib.animation as animation

from pages import defaults
from pages.mouldMonitor import MouldMonitor
from pages.defaults import PLOT_REFRESH_RATE

matplotlib.use("TkAgg")

# initialise the class object holding the window.
app = MouldMonitor(ip_file=defaults.IP_FILE)
# update the graph using the animate method
ani = animation.FuncAnimation(app.f, app.update_plots, interval=PLOT_REFRESH_RATE)
app.initialise_plots()  # initialise the plots with the existing data.
defaults.log.info('Starting running')

while app.is_running():
    # app.update_idletasks()
    app.update()
    if (dt.datetime.now() - app.data_check_time).total_seconds() > defaults.DATA_REFRESH_RATE:
        app.refresh_data()

    if (dt.datetime.now() - app.ip_check_time).total_seconds() > defaults.IP_CHECK_PERIOD:
        app.update_ip_list()
        app.initialise_plots()
        app.list_unreachables(app.button_frame.msg_box)
