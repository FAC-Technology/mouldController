import tkinter as tk
import matplotlib.dates as m_dates
from . import defaults

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TempGraph(tk.Frame):

    def __init__(self, parent, controller, figure):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Mould Heater Readout", font=defaults.LARGE_FONT)
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
