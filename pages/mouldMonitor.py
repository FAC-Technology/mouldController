import datetime as dt
import re
import time
import tkinter as tk

import matplotlib.dates as m_dates
from matplotlib import style
from matplotlib.figure import Figure

from . import defaults
from .buttonPanel import ButtonPanel
from .dacClass import DacClass
from .tempGraph import TempGraph

style.use("ggplot")


class MouldMonitor(tk.Tk):
    # generate the figure, possibly in the wrong place for the class
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
    a.set_xlabel('Clock Time')
    a.set_ylim(15, 110)

    def __init__(self, ip_file, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.running = False
        self.ip_check_time = dt.datetime.now()
        self.data_check_time = dt.datetime.now()
        self.read_ips(ip_file)
        if not self.new_ip_list:
            print('Add a DAC IP to IP_ADDRESSES.txt to begin')
            print(f'Find this file in {defaults.IP_FILE}')
            defaults.log.info(msg='No IPs in list')
            while not self.new_ip_list:
                time.sleep(1)
                self.read_ips(ip_file)
        for ip in self.new_ip_list:
            self.dac_list.append(DacClass(ip))
        self.update_ip_list()
        print('Proceeding when any DAC becomes plottable')
        print('If data exists it is plotted, else new data needs to be gettable')
        dacs_plottable = [False]

        while not any(dacs_plottable):
            dacs_plottable = [dac.connected or dac.temperatureData for dac in self.dac_list]
            if not any(dacs_plottable):
                for dac in self.dac_list:
                    dac.scrape_data()
                    time.sleep(1)
                self.update_ip_list()

        print('Found at least one dac on the network')
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
            if not dac.initialised and dac.temperatureData:
                dac.initialised = True
                self.a.plot_date(defaults.downsample_to_max(dac.timeData, defaults.MAXIMUM_POINTS),  # x list
                                 defaults.downsample_to_max(dac.temperatureData, defaults.MAXIMUM_POINTS),  # y list
                                 defaults.lineStyles[j % len(defaults.lineStyles)],  # line style, loop round
                                 label=dac.name,  # label
                                 xdate=True)
        self.f.legend()

    def refresh_data(self):
        for dac in self.dac_list:
            dac.scrape_data()
            self.data_check_time = dt.datetime.now()
            dac.write_log()

    def update_plots(self, i):
        now = dt.datetime.now()
        self.a.title.set_text(dt.datetime.strftime(now, defaults.TIME_FORMAT))
        for j, dac in enumerate(self.dac_list):
            if dac.active and dac.initialised and not dac.currentPlot:
                self.a.lines[j].set_xdata(defaults.downsample_to_max(dac.timeData, defaults.MAXIMUM_POINTS))
                self.a.lines[j].set_ydata(defaults.downsample_to_max(dac.temperatureData, defaults.MAXIMUM_POINTS))
        left_limit = min([dac.timeData[0] for dac in self.dac_list if dac.timeData])
        right_limit = max([dac.timeData[-1] for dac in self.dac_list if dac.timeData])

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
                if self.running: # only add if panel has been created
                    print('Adding new dac buttons')
                    self.button_list.append({})
                    self.button_list[-1]['name'] = self.dac_list[-1].name
                    self.button_list[-1]['buttons'] = self.button_frame.create_row(self.button_frame, self.dac_list[-1])
                    self.f.legend().remove()

    def list_unreachables(self, msg_box):
        disconnected_list = "! WARNING !\nCould not connect to:\n"
        for dac in self.dac_list:
            if not dac.connected:
                disconnected_list += f"{dac.name}\n"
        if any([not dac.connected for dac in self.dac_list]):  # only display if any disconnects found
            self._write_to_box(msg_box, disconnected_list)
        else:
            self._write_to_box(msg_box, "Connected to all dacs")

    @staticmethod
    def _write_to_box(msg_box, text):
        msg_box.config(state='normal')
        msg_box.delete(1.0, 'end')  # delete lines 1, 2, 3, 4
        msg_box.insert(1.0, f'{text}')
        msg_box.insert(1.0, 'Info\n')
        msg_box.update()
        msg_box.config(state='disabled')
