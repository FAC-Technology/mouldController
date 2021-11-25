import datetime as dt
import math
import os
import psutil
from random import random

from . import defaults
"""
DacClass template is responsible for managing the operations completed 
regarding each individual nanodac controller. 
"""


class DacClass:

    def __init__(self, address):
        self.name = "dac_" + address.split('.')[-1]
        self.address = address
        self.active = True  # each DAC has an 'active' attribute for if the nanodac is currently working.
        self.date = dt.datetime.now().strftime(defaults.DATE_FORMAT)
        self.timeData = []  # in memory time list for plotting
        self.temperatureData = [] # in memory temperature list for plotting
        self.logName = defaults.LOG_FOLDER + "Temperature Log {} {}.csv".format(self.date, self.name)
        self.monitorPass = False
        if os.path.exists(self.logName):
            self.read_log()
        else:
            with open(self.logName, 'w+'):
                pass
        print(f'DAC {self.name} created, initialised with {len(self.temperatureData)} data points')
        self._scalar = random()

    def read_log(self): # read the log file
        with open(self.logName, "r") as f:
            read_data = f.readlines()

        for eachLine in read_data:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                self.timeData.append(dt.datetime.strptime(x, defaults.DATE_FORMAT + '_' + defaults.TIME_FORMAT))
                self.temperatureData.append(float(y))

    def get_data(self):
        temperature = self._scalar * math.sin(0.5*(dt.datetime.now().second +
                                                dt.datetime.now().microsecond*1e-6))
        self.temperatureData.append(temperature)
        self.timeData.append(dt.datetime.now())

    def set_inactive(self):
        print(f'Marking {self.name} as inactive')
        self.active = False
        pass

    def set_active(self):
        print(f'Marking {self.name} as active')
        self.active = True
        pass

    def write_log(self):
        # need to check date in case of increment
        self.date = dt.datetime.now().strftime(defaults.DATE_FORMAT)
        self.logName = defaults.LOG_FOLDER + "Temperature Log {} {}.csv".format(self.date, self.name)

        with open(self.logName, "a+") as f:
            f.write(f"{dt.datetime.strftime(self.timeData[-1],defaults.DATE_FORMAT + '_'+ defaults.TIME_FORMAT)}, \
                        {self.temperatureData[-1]}\n")

    def check_data(self, msg_box):
        if math.sin(self.temperatureData[-1]) > 0:
            self.monitorPass = True
            msg_box.config(state='normal')
            msg_box.delete(1.0, 'end')  # delete lines 1, 2, 3, 4
            msg_box.insert(1.0, f'{self.name} is {self.monitorPass}')
            msg_box.update()
            msg_box.config(state='disabled')

    def export_data(self,msg_box):
        print(f'there you go {self.temperatureData[-1]}')

    def cure_cycle_check(self):
        # calculate max  & min temps at all times
        # check max and min fulfill criteria.
        # this code needs to correspond with the constraints outlined in
        # section 6.1 of 73-011-ATP-(01)-0A-Base_Panel_Cure_Profile


        pass