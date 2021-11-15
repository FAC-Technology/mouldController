import math

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
import time
# from tkinter import ttk
from matplotlib.ticker import MultipleLocator

matplotlib.use("TkAgg")

LARGE_FONT = ("Verdana", 12)
LOG_FOLDER = "logs/"
style.use("ggplot")
lineStyles = ("r--", "g--", "b--", "r:", "g:", "b:", "r-.", "g-.", "b-.")
f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)


def animate(i):
    a.clear()
    a.xaxis.set_major_locator(MultipleLocator(10))

    # app.update()
    a.set_ylabel('Temperature (C)')
    a.set_xlabel('Time (s)')
    now = time.strftime("%H:%M:%S")
    date = time.strftime("%d-%m-%y")
    a.title.set_text(now)
    print('Getting Data')
    # need to append datalogs here
    for m in range(3):
        log_name = LOG_FOLDER + "Temp Log {} Mould {}".format(date,m)
        # section to get data
        temp_val = (m+1)*math.cos(time.time())
        with open(log_name, "a+") as f:
            f.write("{},{}\n".format(now, temp_val))

        x_list = []
        y_list = []

        with open(log_name,"r") as f:
            read_data = f.readlines()

        for eachLine in read_data:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                x_list.append(x)
                y_list.append(float(y))
        # at this point need an x list and a y list

        # section to save data
        import csv

        with open(r'names.csv', 'a', newline='') as csvfile:
            fields = ['first', 'second', 'third']
            with open('name', 'a+') as f:
                writer = csv.writer(f)
                writer.writerow(fields)

        a.plot_date(x_list, y_list, lineStyles[m], label=str(m))


class MouldMonitor(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # tk.Tk.iconbitmap(self, default="Icon path.ico")
        tk.Tk.wm_title(self, "Mould Temperature Manager")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = MonitorPage(container, self)

        self.frames[MonitorPage] = frame
        self.show_frame(MonitorPage)

        frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MonitorPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Mould Heater Readout", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


app = MouldMonitor()
ani = animation.FuncAnimation(f, animate, interval=1000)
# app.mainloop()
while True:
    app.update_idletasks()
    app.update()
