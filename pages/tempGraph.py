import tkinter as tk
import matplotlib.dates as m_dates

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class TempGraph(tk.Frame):

    def __init__(self, parent, controller, figure, font_config):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Mould Heater Readout", font=font_config)
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def setXAxis(self, axes, frequency):
        axes.xaxis.set_major_locator(m_dates.SecondLocator(interval=frequency))