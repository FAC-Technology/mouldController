import tkinter as tk
import re
from matplotlib import style
from matplotlib.figure import Figure
import matplotlib.dates as m_dates
import datetime as dt
import math
import time
from .tempGraph import TempGraph
from .dacClass import DacClass

LARGE_FONT = ("Verdana", 12)

from . import defaults

style.use("ggplot")


class MouldMonitor(tk.Tk):
    _dpi = 100
    _px = 1200
    _py = 600
    f = Figure(figsize=(_px / _dpi, _py / _dpi), dpi=_dpi)
    a = f.add_subplot(111)

    dac_list = []

    def __init__(self, ip_file, *args, **kwargs):
        self.ip_check_time = dt.datetime.now()
        self.old_IP_LIST = self.read_ips(ip_file)
        self.new_IP_LIST = []
        for ip in self.old_IP_LIST:
            self.dac_list.append(DacClass(ip))

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

    def updateDACs(self, new_ip_list):
        for dac in self.dac_list:
            if dac.address not in new_ip_list and dac.active:
                dac.set_inactive()
            elif dac.address in new_ip_list and not dac.active:
                dac.set_active()

        for ip in new_ip_list:
            if ip not in [dac.address for dac in self.dac_list]:
                self.dac_list.append(DacClass(address=ip))

    def animate(self, i):
        now = dt.datetime.now()

        self.a.clear()
        self.a.title.set_text(dt.datetime.strftime(now, defaults.TIME_FORMAT))
        self.a.set_ylabel('Temperature (C)')
        self.a.set_xlabel('Time (s)')
        data_span = 1.0

        for j, dac in enumerate(self.dac_list):
            if dac.active:
                dac.get_data()
                dac.write_log()
                self.a.plot_date(dac.timeData, dac.temperatureData, defaults.lineStyles[j], label=dac.name, xdate=True)

    @staticmethod
    def read_ips(file):
        pattern = re.compile("^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$")
        with open(file, 'r') as f:
            ips = f.read().splitlines()
        ips = list(dict.fromkeys(ips))
        ips = [ip for ip in ips if pattern.match(ip)]
        return ips

    def update_ip_list(self):
        self.ip_check_time = dt.datetime.now()
        self.new_IP_LIST = self.read_ips(defaults.IP_FILE)
        if self.new_IP_LIST != self.old_IP_LIST:
            self.old_IP_LIST = self.new_IP_LIST
            print('Checked IPs, found new addresses')
            self.updateDACs(self.new_IP_LIST)
