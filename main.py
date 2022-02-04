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


# initialise the application
app = MouldMonitor(splash=splash_present)
# update the graph using the animate method
ani = animation.FuncAnimation(app.f, app.update_plots, interval=PLOT_REFRESH_RATE, blit=True)
defaults.log.info('Starting running')

def main():
    while app.is_running():
        t0 = time.time()
        app.update()
        deltaT = round(1000*(time.time() - t0))
        if deltaT > 30:
            print(f'App update took {deltaT} ms')
        with open('updatetimes.txt','a+') as f:
            f.writelines([str(deltaT)+"\n"])
        if (dt.datetime.now() - app.data_check_time).total_seconds() > defaults.DATA_REFRESH_RATE:
            app.refresh_data()

        if (dt.datetime.now() - app.ip_check_time).total_seconds() > defaults.IP_CHECK_PERIOD:
            app.update_dacs()
            app.initialise_plots()
            app.list_unreachables(app.button_frame.msg_box)
        time.sleep(0.2)  # reduces CPU usage


app.after(1000, main)
app.mainloop()