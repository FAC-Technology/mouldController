import tkinter as tk

from matplotlib import style
from matplotlib.figure import Figure
import matplotlib.dates as m_dates
import datetime as dt
import math
import time
from .tempGraph import TempGraph
from .dacClass import DacClass
LARGE_FONT = ("Verdana", 12)

LOG_FOLDER = "mould logs/"
IP_FILE = "IP_ADDRESSES.txt"
IP_CHECK_PERIOD = 0.05 # minutes
DATE_FORMAT = "%d-%m-%y"
TIME_FORMAT = "%H:%M:%S"
style.use("ggplot")
lineStyles = ("r--", "g--", "b--", "r:", "g:", "b:", "r-.", "g-.", "b-.")


class MouldMonitor(tk.Tk):
    _dpi = 100
    _px = 1200
    _py = 600
    f = Figure(figsize=(_px/_dpi, _py/_dpi), dpi=_dpi)
    a = f.add_subplot(111)

    dac_list = []

    def __init__(self, ip_file,*args, **kwargs):
        self._ip_check_time = dt.datetime.now()
        print(self.read_IPs)
        print(ip_file)
        self.old_IP_LIST = self.read_IPs(ip_file)
        for ip in self.old_IP_LIST:
            dac_name = f'dac_{len(self.old_IP_LIST)}'
            self.dac_list.append(DacClass(dac_name, ip))

        tk.Tk.__init__(self, *args, **kwargs)
        self.running = True
        tk.Tk.wm_title(self, "Mould Temperature Manager")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.a.xaxis.set_major_formatter(m_dates.DateFormatter("%H:%M"))

        self.graph_frame = TempGraph(container, self, self.f, LARGE_FONT)
        self.frames[TempGraph] = self.graph_frame
        self.show_frame(TempGraph)
        self.graph_frame.grid(row=0, column=0)

        # text_frame = TempGraph(container, self)
        # self.frames[TempGraph] = text_frame
        # self.show_frame(text_frame)
        # text_frame.grid(row=0, column=1, sticky="nsew")

        exit_button = tk.Button(self, text="Exit", command=self.close)
        exit_button.pack(pady=2)

    def is_running(self):
        return self.running

    def close(self):
        self.running = False
        self.destroy()

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def updateDACs(self,new_IP_list):
        for dac in self.dac_list:
            if dac.address not in new_IP_list and dac.active:
                dac.set_inactive()
            elif dac.address in new_IP_list and not dac.active:
                dac.set_active()

        for ip in new_IP_list:
            if ip not in [dac.address for dac in self.dac_list]:
                dac_name = f'dac_{len(self.dac_list)}'
                self.dac_list.append(DacClass(name=dac_name,IP=ip))

    def animate(self, i):
        # self.a.clear()
        self.a.cla()
        # self.update()

        now = dt.datetime.now()
        date = now.strftime(DATE_FORMAT)
        self.a.title.set_text(dt.datetime.strftime(now, TIME_FORMAT))
        print('Getting Data')
        self.a.set_ylabel('Temperature (C)')
        self.a.set_xlabel('Time (s)')
        data_span = 1.0
        # need to selfend datalogs here
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

            self.a.plot_date(x_list, y_list, lineStyles[m], label=str(m), xdate=True)

            if (x_list[-1] - x_list[0]).total_seconds() > data_span:
                data_span = (x_list[-1] - x_list[0]).total_seconds()

        self.a.set_xlim([x_list[0], x_list[-1]])
        self.graph_frame.setXAxis(self.a,int(0.9*data_span/8))

    def read_IPs(self,file):
        with open(file, 'r') as f:
            ips = f.read().splitlines()

        ips = list(set(ips))
        return ips

    def update_ip_list(self):
        if (dt.datetime.now() - self._ip_check_time).total_seconds() > IP_CHECK_PERIOD * 60:
            self._ip_check_time = dt.datetime.now()
            self.new_IP_LIST = self.read_IPs(IP_FILE)
            if self.new_IP_LIST == self.old_IP_LIST:
                print('no new IPs')
            else:
                self.old_IP_LIST = self.new_IP_LIST
                print('Checked IPs, found new addresses')
                self.updateDACs(self.new_IP_LIST)