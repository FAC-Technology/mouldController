import datetime as dt
import os
import time
import tkinter as tk
import sys

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
    a.set_ylim(0, 110)
    a.xaxis.set_major_formatter(m_dates.DateFormatter("%H:%M"))

    def __init__(self, splash, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.running = False
        self.ip_check_time = dt.datetime(1970, 1, 1)  # initialise a note of when IPs were last checked
        self.data_check_time = dt.datetime(1970, 1, 1)  # initialise a note of when data was last checked
        self.msgbox_update_time = dt.datetime(1970, 1, 1)  # initialise a note of when msgbox was last updated

        self.dac_list = []  # list of all dacs, made from IP_ADDRESSES.txt
        self.old_ip_list = []  # used for comparison
        self.new_ip_list = []  # ip list of DACs
        self.hunter = Hunter()  # create hunter, which in __init__ searches for dacs on network
        if not self.hunter.nds:
            print("Couldn't find any nanodacs, waiting to find one to proceed")

        while not self.hunter.nds:
            self.hunter.populate_list()
            time.sleep(1)
        for nd in self.hunter.nds:
            if nd['name'] not in [nanodac.name for nanodac in self.dac_list]:
                self.dac_list.append(DacClass(name=nd['name'], address=nd['location']))

        if splash:
            pyi_splash.close()

        dacs_plottable = [False]
        while not any(dacs_plottable):
            dacs_plottable = [dac.temperatureData for dac in self.dac_list]
            if not any(dacs_plottable):
                time.sleep(4)
                self.update_dacs()
                for dac in self.dac_list:
                    dac.scrape_data()
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
        updated = False
        for j, dac in enumerate(self.dac_list):
            if not dac.initialised and dac.temperatureData:
                updated = True
                dac.initialised = True
                # make the lists out of a downsampled history + a full res previous 50 points for plotting goodness.
                if len(dac.timeData) > 55:
                    x_list = defaults.downsample_to_max(dac.timeData[:-50], defaults.MAXIMUM_POINTS) \
                             + dac.timeData[-50:]
                    y_list = defaults.downsample_to_max(dac.temperatureData[:-50], defaults.MAXIMUM_POINTS) \
                             + dac.temperatureData[-50:]
                else:
                    x_list = dac.timeData
                    y_list = dac.temperatureData
                print(f"Initialising plot for {dac.name} with {len(x_list)} points.")
                self.a.plot_date(x_list,  # x list
                                 y_list,  # y list
                                 defaults.lineStyles[j % len(defaults.lineStyles)],  # line style, loop round
                                 label=dac.name,  # label
                                 xdate=True)


        if updated:
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
        blits = [self.a.title]
        for j, dac in enumerate(self.dac_list):
            if dac.active and dac.initialised and not dac.currentPlot:
                if False:
                    x_list = defaults.downsample_to_max(dac.timeData[:-50], defaults.MAXIMUM_POINTS) \
                             + dac.timeData[-50:]
                    y_list = defaults.downsample_to_max(dac.temperatureData[:-50], defaults.MAXIMUM_POINTS) \
                             + dac.temperatureData[-50:]
                else:
                    x_list = dac.timeData
                    y_list = dac.temperatureData
                self.a.lines[j].set_xdata(x_list)
                self.a.lines[j].set_ydata(y_list)
                dac.currentPlot = True  # label dac plot as up to date.
                blits.append(self.a.lines[j])

        left_limit = min([dac.timeData[0] for dac in self.dac_list if dac.timeData]) - dt.timedelta(minutes=5) # left limit is left most of any
        right_limit = max([dac.timeData[-1] for dac in self.dac_list if dac.timeData]) + dt.timedelta(minutes=5)  # vice versa for right
        # left_limit = left_limit.replace(microsecond=0, second=0, minute=0, hour=0)
        # right_limit = right_limit.replace(microsecond=0, second=0, minute=0, hour=0)
        # right_limit = right_limit + dt.timedelta(days=1)
        #
        # left_limit = defaults.roundTime(left_limit - dt.timedelta(minutes=5), roundTo=180)  # round to help blitting
        # right_limit = defaults.roundTime(right_limit + dt.timedelta(minutes=5), roundTo=180)  # same
        self.a.set_xlim(left_limit,
                        right_limit)


    def update_dacs(self):
        self.ip_check_time = dt.datetime.now()
        start_time = time.time()
        self.hunter.populate_list()
        print(f'Populating list took {round((time.time() - start_time) * 1e3)}ms')

        for nd in self.hunter.nds:
            for dac in self.dac_list:
                if nd['name'] in [ndac.name for ndac in self.dac_list]:
                    print(f"Updating {dac.name} from {dac.address} to {nd['location']}")
                    dac.address = nd['location']

            if nd['name'] not in [dac.name for dac in self.dac_list]:
                self.dac_list.append(DacClass(name=nd['name'], address=nd['location']))
                defaults.log.info(f"Adding {nd['name']} to list of DACs")
                if self.running:  # only add if panel has been created
                    print('Adding new dac buttons')
                    self.button_list.append({})
                    self.button_list[-1]['name'] = self.dac_list[-1].name
                    self.button_list[-1]['buttons'] = self.button_frame.create_row(self.button_frame, self.dac_list[-1])
                    self.f.legend().remove()

    def list_unreachables(self, msg_box):
        self.msgbox_update_time = dt.datetime.now()
        # the idea here is to keep the user up to date, ensuring all data is live.
        self._write_to_box(msg_box, f"Mould temperatures:"
                                    f"{dt.datetime.strftime(dt.datetime.now(), defaults.TIME_FORMAT)}\n" +
                                    "\n".join([nd.name + ": " +
                                               str(nd.temperatureData[0]) +
                                               f"C (+{(dt.datetime.now() - nd.timeData[-1]).seconds}s)"
                                               for nd in self.dac_list]))

    @staticmethod
    def _write_to_box(msg_box, text):
        msg_box.config(state='normal')
        msg_box.delete(1.0, 'end')  # delete lines 1, 2, 3, 4
        msg_box.insert(1.0, f'{text}')
        msg_box.insert(1.0, 'Info\n')
        msg_box.update()
        msg_box.config(state='disabled')
