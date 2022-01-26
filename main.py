import datetime as dt
import matplotlib
import matplotlib.animation as animation
import time
from pages import defaults
from pages.mouldMonitor import MouldMonitor
from pages.defaults import PLOT_REFRESH_RATE
import cProfile
import pstats

try:
    import pyi_splash
    splash_present = True
except ModuleNotFoundError:
    splash_present = False

matplotlib.use("TkAgg")


def main():
    # initialise the application
    app = MouldMonitor(splash=splash_present)
    # update the graph using the animate method
    ani = animation.FuncAnimation(app.f, app.update_plots, interval=PLOT_REFRESH_RATE)
    app.initialise_plots()  # initialise the plots with the existing data.
    defaults.log.info('Starting running')

    while app.is_running():
        app.update()
        if (dt.datetime.now() - app.data_check_time).total_seconds() > defaults.DATA_REFRESH_RATE:
            app.refresh_data()

        if (dt.datetime.now() - app.ip_check_time).total_seconds() > defaults.IP_CHECK_PERIOD:
            app.update_dacs()
            app.initialise_plots()
            app.list_unreachables(app.button_frame.msg_box)
        time.sleep(0.1)  # reduces CPU usage


with cProfile.Profile() as pr:
    main()
stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats()
