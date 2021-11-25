import tkinter as tk
import re
from matplotlib import style
from matplotlib.figure import Figure
import matplotlib.dates as m_dates
import datetime as dt

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

    def __init__(self, ip_file, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.ip_check_time = dt.datetime.now()
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

        self.graph_frame = TempGraph(container, self, self.f)
        self.button_frame = ButtonPanel(container, self)
        self.frames[TempGraph] = self.graph_frame
        self.frames[ButtonPanel] = self.button_frame

        self.show_frame(TempGraph)
        self.show_frame(ButtonPanel)
        self.graph_frame.grid(row=0, column=0)
        self.button_frame.grid(row=0, column=1)

        exit_button = tk.Button(self, text="Exit", command=self.close)
        exit_button.pack(pady=2)

        self.animate(0)  # do an initial plot call
        self.f.legend()  # allows for clean legend plotting

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

    def animate(self, i):
        now = dt.datetime.now()

        # self.a.clear()
        self.a.title.set_text(dt.datetime.strftime(now, defaults.TIME_FORMAT))
        self.a.set_ylabel('Temperature (C)')
        self.a.set_xlabel('Time (s)')
        data_span = 1.0
        plts = []
        for j, dac in enumerate(self.dac_list):
            if i == 0:
                plts.append(self.a.plot_date(dac.timeData,  # x list
                                             dac.temperatureData,  # y list
                                             defaults.lineStyles[j],  # line style
                                             label=dac.name,  # label
                                             xdate=True)
                            )  # correct as date
            else:
                if dac.active:
                    dac.get_data()
                    dac.write_log()
                    self.a.plot_date(dac.timeData[-1],
                                     dac.temperatureData[-1],
                                     defaults.lineStyles[j],
                                     label=dac.name,
                                     xdate=True
                                     )

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
