import datetime as dt
import math
import time
import tkinter as tk
import matplotlib
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib import style

from pages.mouldMonitor import MouldMonitor

matplotlib.use("TkAgg")

LOG_FOLDER = "logs/"
DATE_FORMAT = "%d-%m-%y"
TIME_FORMAT = "%H:%M:%S"
style.use("ggplot")
lineStyles = ("r--", "g--", "b--", "r:", "g:", "b:", "r-.", "g-.", "b-.")


def animate(i):
    app.a.clear()

    # app.update()
    app.a.set_ylabel('Temperature (C)')
    app.a.set_xlabel('Time (s)')
    now = dt.datetime.now()
    date = now.strftime(DATE_FORMAT)
    app.a.title.set_text(dt.datetime.strftime(now, TIME_FORMAT))
    print('Getting Data')
    data_span = 1.0
    # need to append datalogs here
    for m in range(3):
        log_name = LOG_FOLDER + "Temp Log {} Mould {}.csv".format(date, m)
        # section to get data
        temp_val = (m + 1) * math.log(time.time())
        with open(log_name, "a+") as f:
            f.write("{},{}\n".format(dt.datetime.strftime(now, DATE_FORMAT + TIME_FORMAT), temp_val))
            # f.write("{},{}\n".format(dt.datetime.strftime(now,TIME_FORMAT), temp_val))

        x_list = []
        y_list = []

        with open(log_name, "r") as f:
            read_data = f.readlines()

        for eachLine in read_data:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                x_list.append(dt.datetime.strptime(x, DATE_FORMAT + TIME_FORMAT))
                y_list.append(float(y))
        # at this point need an x list and a y list

        app.a.plot_date(x_list, y_list, lineStyles[m], label=str(m), xdate=True)

        if (x_list[-1] - x_list[0]).total_seconds() > data_span:
            data_span = (x_list[-1] - x_list[0]).total_seconds()
    # print(data_span)
    # if data_span < 60:
    #     tick_frequency = int(60/5)
    #     app.a.xaxis.set_major_locator(mdates.SecondLocator(interval=tick_frequency))
    # elif data_span < 600:
    #     tick_frequency = int(600/5)
    #     app.a.xaxis.set_major_locator(mdates.SecondLocator(interval=tick_frequency))
    # elif data_span > 1000:
    #     tick_frequency = int(data_span/5)
    #     app.a.xaxis.set_major_locator(mdates.SecondLocator(interval=tick_frequency))
    app.a.set_xlim([x_list[0], x_list[-1]])
    app.graph_frame.setXAxis(app.a,int(data_span/5))


app = MouldMonitor()
ani = animation.FuncAnimation(app.f, animate, interval=1000)

while app.is_running():
    app.update_idletasks()
    app.update()
