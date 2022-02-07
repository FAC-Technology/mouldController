import datetime as dt
import matplotlib
import matplotlib.animation as animation
import time
from pages import defaults
from pages.mouldMonitor import MouldMonitor
from pages.defaults import PLOT_REFRESH_RATE

try:
    import pyi_splash
    splash_present = True
except ModuleNotFoundError:
    splash_present = False

matplotlib.use("TkAgg")


# initialise the application
app = MouldMonitor(splash=splash_present)
# update the graph using the animate method
ani = animation.FuncAnimation(app.f, app.update_plots, interval=PLOT_REFRESH_RATE)
defaults.log.info('Starting running')

while app.is_running():
    app.update()  # use Tkinter's update() function to keep things moving

    if (dt.datetime.now() - app.data_check_time).total_seconds() > defaults.DATA_REFRESH_RATE:
        app.refresh_data()

    if (dt.datetime.now() - app.msgbox_update_time).total_seconds() > 4 * defaults.DATA_REFRESH_RATE:
        app.list_unreachables(app.button_frame.msg_box)

    if (dt.datetime.now() - app.ip_check_time).total_seconds() > defaults.IP_CHECK_PERIOD:
        app.update_dacs()
        app.initialise_plots()
    time.sleep(0.05)  # reduces CPU usage

