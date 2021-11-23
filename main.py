import datetime as dt
import math
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


def animate(i):
    # app.a.clear()
    app.a.cla()
    # app.update()

    now = dt.datetime.now()
    date = now.strftime(DATE_FORMAT)
    app.a.title.set_text(dt.datetime.strftime(now, TIME_FORMAT))
    print('Getting Data')
    app.a.set_ylabel('Temperature (C)')
    app.a.set_xlabel('Time (s)')
    data_span = 1.0
    # need to append datalogs here
    for m in range(3):
        log_name = LOG_FOLDER + "Temp Log {} Mould {}.csv".format(date, m)
        # section to get data
        temp_val = (m + 1) * math.log(time.time()-t0)
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

    app.a.set_xlim([x_list[0], x_list[-1]])
    app.graph_frame.setXAxis(app.a,int(data_span/5))


def read_IPs(file):
    with open(file,'r') as f:
        ips = f.read().splitlines()

    ips = list(set(ips))
    return ips


old_IP_LIST = read_IPs(IP_FILE)
app = MouldMonitor(old_IP_LIST)
ani = animation.FuncAnimation(app.f, animate, interval=1000)

log.info('Starting running')
ip_check_time = dt.datetime.now() - dt.timedelta(days=1) # initialise as last checking yesterday

while app.is_running():
    app.update_idletasks()
    app.update()
    if (dt.datetime.now() - ip_check_time).total_seconds() > IP_CHECK_PERIOD * 60:
        ip_check_time = dt.datetime.now()
        new_IP_LIST = read_IPs(IP_FILE)
        if new_IP_LIST == old_IP_LIST:
            log.info(f'Checked IPs, no new found')
        else:
            old_IP_LIST = new_IP_LIST
            log.info(f'Checked IPs, found new addresses')
            print('Checked IPs, found new addresses')
            app.updateDACs(new_IP_LIST)