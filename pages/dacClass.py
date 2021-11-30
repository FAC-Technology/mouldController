import datetime as dt
import math
import os

# import requests
# import urllib
# from lxml import html
# from bs4 import BeautifulSoup as bsoup

from matplotlib import style
from matplotlib.figure import Figure

import pandas as pd
from random import random
from . import cureCycleReqs as ccq
from . import defaults
from .outputPDF import PDF

style.use("ggplot")

"""
DacClass template is responsible for managing the operations completed 
regarding each individual nanodac controller. 
"""


class DacClass:

    def __init__(self, address):
        self.name = "dac_" + address.split('.')[-1]
        self.address = address
        self.active = True  # each DAC has an 'active' attribute for if the nanodac is currently working.
        self.initialised = False  # ensure each DAC is only started once.
        self.date = dt.datetime.now().strftime(defaults.DATE_FORMAT)
        self.timeData = []  # in memory time list for plotting
        self.temperatureData = []  # in memory temperature list for plotting
        self.logName = defaults.LOG_FOLDER + "Temperature Log {} {}.csv".format(self.date, self.name)
        self.monitorPass = False
        self._scalar = random()

        if os.path.exists(self.logName):
            self.read_log(self.logName)
        else:
            with open(self.logName, 'w+'):
                pass
            prev_day = dt.date.today()
            while not self.timeData:  # if list is empty
                prev_day = prev_day - dt.timedelta(days=1)
                prev_log = defaults.LOG_FILE_NAMING.format(prev_day.strftime(defaults.DATE_FORMAT),
                                                           self.name)
                prev_log = defaults.LOG_FOLDER + prev_log
                if os.path.exists(prev_log):
                    defaults.log.info(msg="Reading log from {}".format(prev_log))
                    self.read_log(prev_log)

                if dt.date.today() - prev_day > dt.timedelta(days=7):
                    print('Could not find log file in last week.')
                    self.get_data()

        print(f'DAC {self.name} created, initialised with {len(self.temperatureData)} data points')

    def read_log(self, log_file):  # read the log file
        with open(log_file, "r") as f:
            read_data = f.readlines()

        for eachLine in read_data:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                self.timeData.append(dt.datetime.strptime(x, defaults.DATETIME_FORMAT))
                self.temperatureData.append(float(y))

    def get_data(self):
        temperature = 20 + (self._scalar * math.sin(0.5 * (dt.datetime.now().second +
                                                           dt.datetime.now().microsecond * 1e-6)))
        self.temperatureData.append(temperature)
        self.timeData.append(dt.datetime.now())

    #
    # def scrape_data(self):
    #     url = 'http://time-time.net/timer/digital-clock.php'
    #     sr = requests.session()
    #     page = sr.get(url)
    #     result = html.fromstring(page.content)
    #     time = result.xpath("/html/body/div[2]/div/div[3]/div/div[2]/div[1]")
    #
    #     soup = bsoup(page.content,"html.parser")
    #     # time = soup.find("container", {"class": "timenow"}).get_text(strip=True)
    #     print(time.text)

    def set_active(self):
        # mark DAC as active, and data should be collected and updated
        print(f'Marking {self.name} as active')
        self.active = True
        pass

    def set_inactive(self):
        # disable DAC so no data is being retrieved anymore.
        print(f'Marking {self.name} as inactive')
        self.active = False
        pass

    def write_log(self):
        # need to check date in case of increment
        self.date = dt.datetime.now().strftime(defaults.DATE_FORMAT)
        self.logName = defaults.LOG_FOLDER + defaults.LOG_FILE_NAMING.format(self.date, self.name)

        with open(self.logName, "a+") as f:
            f.write(f"{dt.datetime.strftime(self.timeData[-1], defaults.DATETIME_FORMAT)}, \
                        {self.temperatureData[-1]}\n")

    def check_data(self, msg_box):
        monitor_output = self._assemble_check_string(self.cure_cycle_check_corner_method())
        if self.monitorPass:
            self._write_to_box(msg_box, monitor_output)

        elif isinstance(monitor_output, type(None)):
            msg = f'No cure cycle results for {self.name}\n Probably not enough time data to search'
            self._write_to_box(msg_box,msg)

        else:
            self._write_to_box(msg_box,monitor_output)

    def export_data(self, msg_box):
        # method gets the cure results, and writes a graph to a file in mould temp exports as a .png
        # the .png is then written to a .pdf which also has some info about what happened as a more descriptive
        # output than what went exactly in the cure cycle.
        # if the cure cycle was a failure, it just prints the graph of all temperature history stored in memory
        now = dt.datetime.now()

        _dpi = 100
        _px = 1200
        _py = 600
        f = Figure(figsize=(_px / _dpi,
                            _py / _dpi),
                   dpi=_dpi)
        a = f.add_subplot(111)
        a.set_ylabel('Temperature (C)')
        a.set_xlabel('Time (s)')

        cure_results = self.cure_cycle_check_corner_method()
        # cure results is a list:
        # [cureSuccess?,[times],postcureSuccess?,[PCtimes]]
        def nearest(items, pivot):
            return min(items, key=lambda x: abs(x - pivot))

        if cure_results[0] and cure_results[2]:
            start_graph_time = cure_results[1][0] - dt.timedelta(minutes=20)
            end_graph_time = cure_results[3][-1] + dt.timedelta(minutes=20)
            start_index = self.timeData.index(nearest(self.timeData, start_graph_time))
            end_index = self.timeData.index(nearest(self.timeData, end_graph_time))
            x_data = self.timeData[start_index:end_index]
            y_data = self.temperatureData[start_index:end_index]
            a.title.set_text(f'Cure Results for {self.name} between {dt.datetime.strftime(start_graph_time, defaults.TIME_FORMAT)} and '
                             f'{dt.datetime.strftime(end_graph_time, defaults.TIME_FORMAT)}')
        else:
            x_data = self.timeData
            y_data = self.temperatureData
            a.title.set_text(f'Time history for {self.name}, no cure cycle was detected')

        a.plot_date(x_data,
                    y_data,
                    'k-',
                    label=self.name,  # label
                    xdate=True)
        details_text = self._assemble_check_string(cure_results)

        print(f'there you go {self.temperatureData[-1]}')

        out_graph_name = os.path.join(defaults.EXPORT_PATH,
                               defaults.GRAPH_EXPORT_NAME.format(self.name,
                                                                 now.strftime(defaults.FNAME_TIME_FORMAT)))
        f.savefig(out_graph_name)

        out_file = PDF(title=self.name,
                       logo=defaults.LOGO_FILE)
        out_file.add_page()
        out_file.insert_graph(graph_loc=out_graph_name+'.png')
        out_file.output(out_graph_name + '.pdf')
        self._write_to_box(msg_box, f'Output PDF to {out_graph_name}')

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
        if (self.timeData[-1] - self.timeData[0]).total_seconds() < ccq.B_A:
            return [cured, cure_window_times, post_cured, post_cure_times]

        df = pd.DataFrame({'Datetime': self.timeData, 'temperature': self.temperatureData})
        df['Datetime'] = pd.to_datetime(df['Datetime'], format=defaults.DATETIME_FORMAT)
        df = df.set_index(pd.DatetimeIndex(df['Datetime'])).resample(f'{average_window}H').ffill()

        i = len(df)

        while not post_cured:
            i -= 1
            if i < 0:
                break
            if ccq.postcure_bounds(df['temperature'][i]) and not post_cure_entered:
                post_cure_entered = True
                post_cure_times.insert(0, df.temperature.index[i])

            if not ccq.postcure_bounds(df['temperature'][i]) and post_cure_entered:
                post_cure_entered = False
                post_cure_times.insert(0, df.temperature.index[i])

            if len(post_cure_times) % 2 == 0 and post_cure_times:
                if (post_cure_times[-1] - post_cure_times[0]).total_seconds() > ccq.D_C:
                    post_cured = True
            elif post_cure_times:
                if (post_cure_times[-1] - post_cure_times[0]).total_seconds() > ccq.D_C:
                    post_cured = False
                    break

        while not cured:
            i -= 1
            if i < 0:
                break
            if ccq.cure_bounds(df['temperature'][i]) and not cure_window_entered:
                cure_window_entered = True
                cure_window_times.insert(0, df.temperature.index[i])

            if not ccq.cure_bounds(df['temperature'][i]) and cure_window_entered:
                cure_window_entered = False
                cure_window_times.insert(0, df.temperature.index[i])

            if len(cure_window_times) % 2 == 0 and cure_window_times and \
                    (cure_window_times[-1] - cure_window_times[0]).total_seconds() > ccq.B_A:
                cured = True
            elif cure_window_times:
                if (cure_window_times[-1] - cure_window_times[0]).total_seconds() > ccq.B_A:
                    break
        return [cured, cure_window_times, post_cured, post_cure_times]

    @staticmethod
    def _assemble_check_string(check_outcome):
        ret_string = ""
        if check_outcome[0]:
            cure_start_stop = (check_outcome[1][-1] - check_outcome[1][0]).total_seconds() / 60
            ret_string += f"Panel is cured, and spent {round(cure_start_stop)} minutes at temperature.\n"
            if len(check_outcome[1]) > 2:
                interrupt_times = "\n".join([str(t.time()) for t in check_outcome[1][1:-1:1]])
                ret_string += f"It left the cure window between the following times:\n {interrupt_times}"
            return ret_string
        else:
            ret_string += 'No cure cycle detected'

    @staticmethod
    def _write_to_box(msg_box, text):
        msg_box.config(state='normal')
        msg_box.delete(1.0, 'end')  # delete lines 1, 2, 3, 4
        msg_box.insert(1.0, f'{text}')
        msg_box.insert(1.0, 'Info\n')
        msg_box.update()
        msg_box.config(state='disabled')