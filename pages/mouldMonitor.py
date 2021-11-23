import tkinter as tk
# from monitorPage import MonitorPage
from matplotlib.figure import Figure
import matplotlib.dates as m_dates

from .tempGraph import TempGraph
LARGE_FONT = ("Verdana", 12)


class MouldMonitor(tk.Tk):

    f = Figure(figsize=(5, 5), dpi=150)
    a = f.add_subplot(111)

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.running = True
        # tk.Tk.iconbitmap(self, default="Icon path.ico")
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
