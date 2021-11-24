import datetime as dt
import math
import os
from . import defaults

class DacClass:

    def __init__(self, address):
        self.name = "dac_" + address.split('.')[-1]
        self.address = address
        self.active = True
        self.date = dt.datetime.now().strftime(defaults.DATE_FORMAT)
        self.timeData = []
        self.temperatureData = []
        self.logName = defaults.LOG_FOLDER + "Temperature Log {} Mould {}.csv".format(self.date, self.name)
        if os.path.exists(self.logName):
            self.read_log()
        else:
            with open(self.logName, 'w+'):
                pass
            print(f'DAC {self.name} created, initialised with {len(self.temperatureData)} data points')

    def read_log(self):
        with open(self.logName, "r") as f:
            read_data = f.readlines()

        for eachLine in read_data:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                self.timeData.append(dt.datetime.strptime(x, defaults.DATE_FORMAT + '_'+ defaults.TIME_FORMAT))
                self.temperatureData.append(float(y))

    def get_data(self):
        temperature = math.sin(dt.datetime.now().second)

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
        with open(self.logName, "a+") as f:
            f.write(f"{dt.datetime.strftime(self.timeData[-1],defaults.DATE_FORMAT +'_'+ defaults.TIME_FORMAT)}, {self.temperatureData[-1]}\n")

