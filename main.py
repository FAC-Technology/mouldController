import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
import time
# from tkinter import ttk
matplotlib.use("TkAgg")

LARGE_FONT = ("Verdana", 12)
style.use("ggplot")
lineStyles = ("b--", "b:", "b-.", "r--", "r:", "r-.", "g--", "g:", "g-.")
f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)


def animate(i):
    a.clear()
    # app.update()
    a.set_ylabel('Temperature (C)')
    a.set_xlabel('Time (s)')
    now = time.strftime("%H:%M:%S")
    a.title.set_text(now)
    print('Getting Data')
    # need to append datalogs here
    for m in range(3):
        # section to get data
        with open("sampleText{}.txt".format(m+1), "r") as f:
            pull_data = f.read()
        data_list = pull_data.split('\n')
        x_list = []
        y_list = []
        for eachLine in data_list:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                x_list.append(int(x))
                y_list.append(int(y))
        # at this point need an x list and a y list

        # section to save data
        import csv

        with open(r'names.csv', 'a', newline='') as csvfile:
            fields = ['first', 'second', 'third']
            with open(r'name', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(fields)
        a.plot(x_list, y_list, label=str(m))


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
