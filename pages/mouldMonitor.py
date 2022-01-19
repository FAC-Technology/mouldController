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
from .hunterClass import Hunter
try:
    import pyi_splash
    splash_present = True
except ModuleNotFoundError:
    splash_present = False

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
    a.set_ylabel('Temperature (C)')
    a.set_xlabel('Clock Time')
    a.set_ylim(15, 110)
    a.xaxis.set_major_formatter(m_dates.DateFormatter("%H:%M"))

    def __init__(self, splash, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.running = False
        self.ip_check_time = dt.datetime(1970, 1, 1)  # initialise a note of when IPs were last checked
        self.data_check_time = dt.datetime(1970, 1, 1)  # initialise a note of when data was last checked

        self.dac_list = []  # list of all dacs, made from IP_ADDRESSES.txt
        self.old_ip_list = []  # used for comparison
        self.new_ip_list = []  # ip list of DACs
        self.hunter = Hunter()  # create hunter, which in __init__ searches for dacs on network
        if self.hunter.found_count == 0:
            print("Couldn't find any nanodacs, waiting to find one to proceed")

        while self.hunter.found_count == 0:
            self.hunter.populate_list()
            time.sleep(1)
        for nd in self.hunter.nds:
            self.dac_list.append(DacClass(name=nd['name'], address=nd['location']))

        if splash:
            pyi_splash.close()

        dacs_plottable = [False]
        while not any(dacs_plottable):
            dacs_plottable = [dac.temperatureData for dac in self.dac_list]
            if not any(dacs_plottable):
                for dac in self.dac_list:
                    dac.scrape_data()
                    time.sleep(1)
                self.update_ip_list()

        print('Found at least one dac to plot')
        self.running = True
        # title
        tk.Tk.wm_title(self, "Mould Temperature Manager")
        # box in which to put everything
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        # create interfaces
        self.graph_frame = TempGraph(container, self, self.f)
        self.button_frame = ButtonPanel(container)
        self.frames[TempGraph] = self.graph_frame
        self.frames[ButtonPanel] = self.button_frame
        self.frames[TempGraph].tkraise()
        self.frames[ButtonPanel].tkraise()

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
            l1 = len(dac.temperatureData)
            dac.scrape_data()
            self.data_check_time = dt.datetime.now()
            l2 = len(dac.temperatureData)
            if l2 > l1:
                dac.write_log()  # only write to log if data is actually longer now

    def update_plots(self, i):
        now = dt.datetime.now()
        self.a.title.set_text(dt.datetime.strftime(now, defaults.TIME_FORMAT))
        for j, dac in enumerate(self.dac_list):
            if dac.active and dac.initialised and not dac.currentPlot:
                self.a.lines[j].set_xdata(defaults.downsample_to_max(dac.timeData, defaults.MAXIMUM_POINTS))
                self.a.lines[j].set_ydata(defaults.downsample_to_max(dac.temperatureData, defaults.MAXIMUM_POINTS))
                dac.currentPlot = True  # label dac plot as up to date.
        left_limit = min([dac.timeData[0] for dac in self.dac_list if dac.timeData])
        right_limit = max([dac.timeData[-1] for dac in self.dac_list if dac.timeData])

        self.a.set_xlim(left_limit - dt.timedelta(minutes=5),
                        right_limit + dt.timedelta(minutes=5))


    def update_dacs(self):
        self.ip_check_time = dt.datetime.now()
        self.hunter.populate_list()
        for nd in self.hunter.nds:
            if nd['location'] not in [dac.address for dac in self.dac_list]:
                self.dac_list.append(DacClass(name=nd['name'], address=nd['location']))
                defaults.log.info(f"Adding {nd['name']} to list of DACs")
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
