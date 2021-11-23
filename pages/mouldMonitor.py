import tkinter as tk
from matplotlib.figure import Figure
import matplotlib.dates as m_dates

from .tempGraph import TempGraph
from .dacClass import DacClass
LARGE_FONT = ("Verdana", 12)


class MouldMonitor(tk.Tk):
    _dpi = 100
    _px = 1200
    _py = 600
    f = Figure(figsize=(_px/_dpi, _py/_dpi), dpi=_dpi)
    a = f.add_subplot(111)

    dac_list = []

    def __init__(self, dac_IPs, *args, **kwargs):

        for ip in dac_IPs:
            dac_name = f'dac_{len(self.dac_list)}'
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
