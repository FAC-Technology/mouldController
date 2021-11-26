import datetime as dt
import math
import os

import pandas as pd
from random import random
from . import cureCycleReqs as ccq
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
        self.temperatureData = []  # in memory temperature list for plotting
        self.logName = defaults.LOG_FOLDER + "Temperature Log {} {}.csv".format(self.date, self.name)
        self.monitorPass = False
        if os.path.exists(self.logName):
            self.read_log()
        else:
            with open(self.logName, 'w+'):
                pass
        print(f'DAC {self.name} created, initialised with {len(self.temperatureData)} data points')
        self._scalar = random()

    def read_log(self):  # read the log file
        with open(self.logName, "r") as f:
            read_data = f.readlines()

        for eachLine in read_data:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                self.timeData.append(dt.datetime.strptime(x, defaults.DATE_FORMAT + '_' + defaults.TIME_FORMAT))
                self.temperatureData.append(float(y))

    def get_data(self):
        temperature = 20 + (self._scalar * math.sin(0.5 * (dt.datetime.now().second +
                                                           dt.datetime.now().microsecond * 1e-6)))
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
            pass
            # f.write(f"{dt.datetime.strftime(self.timeData[-1], defaults.DATE_FORMAT + '_' + defaults.TIME_FORMAT)}, \
            #             {self.temperatureData[-1]}\n")

    def check_data(self, msg_box):
        self.monitorPass = self._assemble_check_string(self.cure_cycle_check_corner_method())
        if self.monitorPass:
            msg_box.config(state='normal')
            msg_box.delete(1.0, 'end')  # delete lines 1, 2, 3, 4
            msg_box.insert(1.0, f'{self.monitorPass}')
            msg_box.insert(1.0, 'Info\n')
            msg_box.update()
            msg_box.config(state='disabled')
        else:
            msg_box.config(state='normal')
            msg_box.delete(1.0, 'end')  # delete lines 1, 2, 3, 4
            msg_box.insert(1.0, f'{self.monitorPass}')
            msg_box.insert(1.0, 'Info\n')
            msg_box.update()
            msg_box.config(state='disabled')

    def export_data(self, msg_box):
        print(f'there you go {self.temperatureData[-1]}')

    def cure_cycle_check_integral_method(self):
        # calculate max  & min temps at all times
        # check max and min fulfill criteria.
        temp_floor = 65
        integral_target = ccq.B_A * (ccq.Emin - temp_floor) + ccq.D_C * (ccq.Fmin - temp_floor)
        result = False
        integral = 0
        inc = -1
        while integral < integral_target:
            if inc <= -len(self.timeData):
                print('Ran out of data')
                break
            inc -= 1
            delta_t = (self.timeData[inc] - self.timeData[inc - 1]).total_seconds()
            if delta_t > 10:
                delta_t = 0
            integral += self.temperatureData[inc] * delta_t
            if integral > integral_target:
                result = True
                print('Cured')
            else:
                print(f'integral target {integral_target}, integral={integral}')

                break
        return result

    def cure_cycle_check_corner_method(self):
        # go back in time and find each corner,
        # with a moving average of the max and min
        # document every time temp profile enters and leaves windows
        # considers success when an even list of times has a start and end time
        # longer than the required time.
        average_window = 0.05
        post_cured = False
        post_cure_entered = False
        post_cure_times = []  # an even numbered list of entry / exit times to the post_cure window

        cured = False
        cure_window_entered = False
        cure_window_times = []

        df = pd.DataFrame({'Datetime': self.timeData, 'temperature': self.temperatureData})
        df_format = defaults.DATE_FORMAT + '_' + defaults.TIME_FORMAT
        df['Datetime'] = pd.to_datetime(df['Datetime'], format=df_format)
        df = df.set_index(pd.DatetimeIndex(df['Datetime'])).resample(f'{average_window}H').ffill()
        # df = df

        i = len(df)
        while not post_cured:
            i -= 1
            if i < 0:
                print('Could not detect post cure')
                break
            if ccq.postcure_bounds(df['temperature'][i]) and not post_cure_entered:
                post_cure_entered = True
                post_cure_times.insert(0, df.temperature.index[i])

            if post_cure_entered:
                if not ccq.postcure_bounds(df['temperature'][i]):
                    post_cure_entered = False
                    post_cure_times.insert(0, df.temperature.index[i])

            if len(post_cure_times) % 2 == 0 and len(post_cure_times) > 0:
                if (post_cure_times[-1] - post_cure_times[0]).total_seconds() > ccq.D_C:
                    post_cured = True
            elif len(post_cure_times) > 0:
                if (post_cure_times[-1] - post_cure_times[0]).total_seconds() > ccq.D_C:
                    post_cured = False
                    break

        while not cured:
            i -= 1
            if i < 0:
                print('Could not detect cure')
                break
            print(df['temperature'][i])
            a = df.temperature.index[i]
            if ccq.cure_bounds(df['temperature'][i]) and not cure_window_entered:
                cure_window_entered = True
                cure_window_times.insert(0,df.temperature.index[i])

            if cure_window_entered:
                if not ccq.cure_bounds(df['temperature'][i]):
                    cure_window_entered = False
                    cure_window_times.insert(0, df.temperature.index[i])

            if len(cure_window_times) % 2 == 0 and len(cure_window_times) > 0 and \
                    (cure_window_times[-1] - cure_window_times[0]).total_seconds() > ccq.B_A:
                cured = True
            elif len(cure_window_times) > 0:
                if (cure_window_times[-1] - cure_window_times[0]).total_seconds() > ccq.B_A:
                    break
        return [cured, cure_window_times, post_cured, post_cure_times]

    def _assemble_check_string(self, check_outcome):
        ret_string = ""
        print(check_outcome)
        if check_outcome[0]:
            cure_start_stop = (check_outcome[1][-1] - check_outcome[1][0]).total_seconds()/60
            ret_string += f"Panel is cured, and spent {round(cure_start_stop)} minutes at temperature.\n"
            if len(check_outcome[1]) > 2:
                interrupt_times = "\n".join([str(t.time()) for t in check_outcome[1][1:-1:1]])
                ret_string += f"It left the cure window between the following times:\n {interrupt_times}"
            return ret_string
