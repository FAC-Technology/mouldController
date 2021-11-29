import tkinter as tk
import re
from matplotlib import style
from matplotlib.figure import Figure
import matplotlib.dates as m_dates
import datetime as dt
from collections import deque
import time
from .tempGraph import TempGraph
from .buttonPanel import ButtonPanel
from .dacClass import DacClass
from . import defaults

style.use("ggplot")


class MouldMonitor(tk.Tk):
    _dpi = 100
    _px = 1200
    _py = 600
    f = Figure(figsize=(_px / _dpi,
                        _py / _dpi),
               dpi=_dpi)
    a = f.add_subplot(111)

    dac_list = []
    old_ip_list = []
    new_ip_list = []

    a.set_ylabel('Temperature (C)')
    a.set_xlabel('Time (s)')

    def __init__(self, ip_file, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.ip_check_time = dt.datetime.now()
        self.read_ips(ip_file)
        while not self.new_ip_list:
            print('Add a DAC IP to IP_ADDRESSES.txt to begin')
            defaults.log.info(msg='No IPs in list')
            time.sleep(5)
            self.read_ips(ip_file)

        for ip in self.new_ip_list:
            self.dac_list.append(DacClass(ip))

        self.running = True
        tk.Tk.wm_title(self, "Mould Temperature Manager")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        self.a.xaxis.set_major_formatter(m_dates.DateFormatter("%H:%M"))
        self.plts = []

        self.graph_frame = TempGraph(container, self, self.f)
        self.button_frame = ButtonPanel(container)
        self.frames[TempGraph] = self.graph_frame
        self.frames[ButtonPanel] = self.button_frame

        self.show_frame(TempGraph)
        self.show_frame(ButtonPanel)
        self.graph_frame.grid(row=0, column=0)
        self.button_frame.grid(row=0, column=1)

        exit_button = tk.Button(self, text="Exit", command=self.close)
        exit_button.pack(pady=2)

        self.button_list = []
        for dac in self.dac_list:
            self.button_list.append({})
            self.button_list[-1]['name'] = dac.name
            self.button_list[-1]['buttons'] = self.button_frame.create_row(self.button_frame, dac)

    def is_running(self):
        return self.running

    def close(self):
        self.running = False
        self.destroy()

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def initialise_plots(self):
        for j, dac in enumerate(self.dac_list):
            self.a.plot_date(dac.timeData,  # x list
                             dac.temperatureData,  # y list
                             defaults.lineStyles[j],  # line style
                             label=dac.name,  # label
                             xdate=True)

    def animate(self, i):
        now = dt.datetime.now()
        self.a.title.set_text(dt.datetime.strftime(now, defaults.TIME_FORMAT))
        for j, dac in enumerate(self.dac_list):
            # print('scraping')
            # dac.scrape_data()
            # print('finished')
            if dac.active:
                dac.get_data()
                dac.write_log()
                self.a.lines[j].set_xdata(dac.timeData)
                self.a.lines[j].set_ydata(dac.temperatureData)

        left_limit = min([dac.timeData[0] for dac in self.dac_list])
        right_limit = max([dac.timeData[-1] for dac in self.dac_list])

        self.a.set_xlim(left_limit - dt.timedelta(minutes=1),
                        right_limit + dt.timedelta(minutes=1))

    def read_ips(self, file):
        pattern = re.compile("^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$")  # regexp magic to check IP format
        with open(file, 'r') as f:
            ips = f.read().splitlines()
        ips = list(dict.fromkeys(ips))
        self.new_ip_list = [ip for ip in ips if pattern.match(ip)]  # remove all non-conforming lines

    def update_ip_list(self):
        self.ip_check_time = dt.datetime.now()
        self.read_ips(defaults.IP_FILE)
        if self.new_ip_list != self.old_ip_list:
            print('Updating DACs')
            self.old_ip_list = self.new_ip_list
            self.updateDACs(self.new_ip_list)

    def updateDACs(self, new_ip_list):
        for dac in self.dac_list:
            if dac.address not in new_ip_list and dac.active:
                dac.set_inactive()
            elif dac.address in new_ip_list and not dac.active:
                dac.set_active()

        for ip in new_ip_list:
            if ip not in [dac.address for dac in self.dac_list]:
                self.dac_list.append(DacClass(address=ip))
                defaults.log.info(f'Adding {ip} to list of DACs')
                print('Adding new dac buttons')
                self.button_list.append({})
                self.button_list[-1]['name'] = self.dac_list[-1].name
                self.button_list[-1]['buttons'] = self.button_frame.create_row(self.button_frame, self.dac_list[-1])
                self.f.legend().remove()
