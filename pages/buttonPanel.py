import tkinter as tk
from . import defaults


class ButtonPanel(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # label = tk.title(self, text="Heater Management", font=defaults.LARGE_FONT)
        self.button_rows = []
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.msg_box = tk.Text(
                self,
                height=14,
                width=30,
                font=defaults.SMALL_FONT,
                wrap=tk.WORD
            )
        self.msg_box.insert('end', 'Info')
        self.msg_box.config(state='disabled')
        self.msg_box.grid(row=0, columnspan=2)

    def create_row(self, parent, dac):
        self.button_rows.append({})
        self.button_rows[-1]['monitor'] = tk.Button(master=parent,
                                                    text=f'Monitor {dac.name}',
                                                    command=lambda: dac.check_data(self.msg_box))
        self.button_rows[-1]['export'] = tk.Button(master=parent,
                                                   text=f'Export {dac.name}',
                                                   command=lambda: dac.export_data(self.msg_box))

        parent.grid_rowconfigure(len(self.button_rows), weight=1)
        parent.grid_columnconfigure(2, weight=1)
        for i, b in enumerate(self.button_rows[-1].items()):
            b[1].grid(row=len(self.button_rows), column=i)

