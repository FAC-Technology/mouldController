import tkinter as tk

class MonitorPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Mould Heater Readout", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
