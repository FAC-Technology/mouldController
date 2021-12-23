import datetime as dt
import math
import os
import re
from random import random

import matplotlib.dates as mdates
import matplotlib.patches as patches

import requests
from matplotlib import style
from matplotlib.figure import Figure

from . import cureCycleReqs as ccq
from . import defaults

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
        self.logName = os.path.join(defaults.LOG_FOLDER, defaults.LOG_FILE_NAMING.format(self.date, self.name))
        self.fullLogName = os.path.join(defaults.LOG_FOLDER, defaults.FULL_LOG_FILE_NAMING.format(self.date, self.name))
        self.monitorPass = False
        self._scalar = 20 * random()
        self._user = "admin"
        self._pwd = "qqqqqqq/"
        self._logMemory = 0  # used to count how many days in the past a log has been searched for
        self.connected = False
        self.currentPlot = True

        if os.path.exists(self.logName):
            self.read_log(self.logName)
        else:
            with open(self.logName, 'w+'):
                pass
            self.scrape_data()

        print(f'DAC {self.name} created, initialised with {len(self.temperatureData)} data points')

    def read_log(self, log_file):  # read the log file
        with open(log_file, "r") as f:
            read_data = f.readlines()

        for eachLine in read_data:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                self.timeData.append(dt.datetime.strptime(x, defaults.DATETIME_FORMAT))
                self.temperatureData.append(float(y))

    def add_previous_log(self, msg_box):
        self._logMemory += 1
        prev_day = dt.date.today() - dt.timedelta(days=self._logMemory)
        prev_day = prev_day
        prev_log_name = defaults.LOG_FILE_NAMING.format(prev_day.strftime(defaults.DATE_FORMAT),
                                                        self.name)
        prev_log = os.path.join(defaults.LOG_FOLDER, prev_log_name)

        if os.path.isfile(prev_log):
            prev_time_space = []
            prev_temperature_space = []

            self._write_to_box(msg_box, f"Found log for {prev_day.strftime(defaults.DATE_FORMAT)}")
            with open(prev_log, "r") as f:
                read_data = f.readlines()

            for eachLine in read_data:
                if len(eachLine) > 1:
                    x, y = eachLine.split(',')
                    prev_time_space.append(dt.datetime.strptime(x, defaults.DATETIME_FORMAT))
                    prev_temperature_space.append(float(y))
            self.timeData = prev_time_space + self.timeData
            self.temperatureData = prev_temperature_space + self.temperatureData
            self.currentPlot = False
        else:
            self._write_to_box(msg_box, f"Couldn't find log for {prev_day.strftime(defaults.DATE_FORMAT)}")

    def get_data(self):  # legacy function to generate temp data without a DAC
        if dt.datetime.now().microsecond > 5e5:
            temperature = 71 + (self._scalar * math.sin(0.2 * (dt.datetime.now().second +
                                                               dt.datetime.now().microsecond * 1e-6)))
            self.currentPlot = False
            self.temperatureData.append(temperature)
            self.timeData.append(dt.datetime.now())

    def scrape_data(self):  # extracts numerical data request from nanodac on network

        cookies = {
            'session': '(null)',
        }
        headers = {
            'Connection': 'close',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/96.0.4664.45 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'http://{self.address}/npage.html',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,de;q=0.7',
        }
        try:
            response = requests.get(f'http://{self.address}/numerics',
                                    headers=headers,
                                    cookies=cookies,
                                    auth=(self._user, self._pwd),
                                    verify=False,
                                    timeout=0.1)
        except requests.exceptions.ConnectTimeout:
            self.connected = False
            defaults.log.info(msg=f"Couldn't reach {self.name}, connection error")
            return

        if response.status_code == 200:
            temp_positions = [7, 10, 13, 16]  # positions in the string of temperature values
            print(response.text)
            temp_string = re.findall('\d*\.?\d+', response.text.split(',')[7])[0]
            try:
                temperature = float(temp_string)
                self.connected = True
                self.temperatureData.append(temperature)
                self.timeData.append(dt.datetime.now())
                all_temps = []
                for indx in temp_positions:
                    try:
                        all_temps.append(re.findall('\d*\.?\d+', response.text.split(',')[indx])[0])
                    except IndexError:
                        all_temps.append('NaN')
                with open(self.fullLogName, "a+") as f:
                    f.write(f"{dt.datetime.strftime(self.timeData[-1], defaults.DATETIME_FORMAT)}, \
                                {all_temps}\n")
                self.currentPlot = False
            except IndexError:
                self.connected = False
                defaults.log.info(msg=f"Couldn't reach {self.name}, connection error. Possible thermocouple issue.")
            except ValueError:
                self.connected = False
                defaults.log.info(msg=f"Couldn't reach {self.name}, connection error")


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
        self.logName = os.path.join(defaults.LOG_FOLDER, defaults.LOG_FILE_NAMING.format(self.date, self.name))
        if self.temperatureData:
            with open(self.logName, "a+") as f:
                f.write(f"{dt.datetime.strftime(self.timeData[-1], defaults.DATETIME_FORMAT)}, \
                            {self.temperatureData[-1]}\n")

    def check_data(self, msg_box):
        if len(self.temperatureData) < 5:
            msg = f'Not enough data for analysis on {self.name}.\n'
            self._write_to_box(msg_box, msg)
            return

        monitor_output = self._assemble_check_string(self.cure_cycle_check_corner_method())
        if self.monitorPass:
            self._write_to_box(msg_box, monitor_output)

        elif isinstance(monitor_output, type(None)):
            msg = f'No cure cycle detected for {self.name}.\n'
            self._write_to_box(msg_box, msg)

        else:
            self._write_to_box(msg_box, monitor_output)

    def export_data(self, msg_box):
        # method gets the cure results, and writes a graph to a file in mould temp exports as a .png
        # the .png is then written to a .pdf which also has some info about what happened as a more descriptive
        # output than what went exactly in the cure cycle.
        # if the cure cycle was a failure, it just prints the graph of all temperature history stored in memory
        if len(self.temperatureData) < 5:
            msg = f'Not enough data for export on {self.name}\n.'
            self._write_to_box(msg_box, msg)
            return
        now = dt.datetime.now()

        _dpi = 100
        _px = 1200
        _py = 600
        f = Figure(figsize=(_px / _dpi,
                            _py / _dpi),
                   dpi=_dpi)
        a = f.add_subplot(111)

        a.set_ylabel('Temperature (C)')
        a.set_xlabel('Clock Time')
        a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        cure_results = self.cure_cycle_check_corner_method()
        a.set_ylim(15, 110)

        # cure results is a list:
        # [cureSuccess?,[times],postcureSuccess?,[PCtimes]]

        def nearest(items, pivot):
            return min(items, key=lambda x: abs(x - pivot))
        title_text = f"{self.name} cure cycle results:\n"
        if cure_results[0] and cure_results[2]:
            start_graph_time = cure_results[1][0] - dt.timedelta(minutes=20)
            end_graph_time = cure_results[3][-1] + dt.timedelta(minutes=20)
            start_index = self.timeData.index(nearest(self.timeData, start_graph_time))
            end_index = self.timeData.index(nearest(self.timeData, end_graph_time))
            x_data = self.timeData[start_index:end_index]
            y_data = self.temperatureData[start_index:end_index]
            a.title.set_text(
                f'Cure Results for {self.name} between {dt.datetime.strftime(start_graph_time, defaults.TIME_FORMAT)} '
                f'and '
                f'{dt.datetime.strftime(end_graph_time, defaults.TIME_FORMAT)}')

        if cure_results[0]:  #
            rect_cure = patches.Rectangle((mdates.date2num(cure_results[1][0]),
                                           ccq.Emin),
                                          ccq.B_A / (24 * 3600),
                                          # mdates.date2num(dt.timedelta(seconds=ccq.B_A)), # width
                                          ccq.Emax - ccq.Emin,  # height
                                          color='g',
                                          alpha=0.2
                                          )
            a.add_patch(rect_cure)
            title_text += f"Cured between {cure_results[1][0]} and {cure_results[1][-1]}\n"
        else:
            title_text += "Could not find cure.\n"

        if cure_results[2]:
            rect_postcure = patches.Rectangle(  # draw rectangles on graph if
                (mdates.date2num(cure_results[3][0]),
                 ccq.Fmin),
                ccq.D_C / (24 * 3600),  # width
                ccq.Fmax - ccq.Fmin,  # height
                color='r',
                alpha=0.2
            )
            a.add_patch(rect_postcure)

            title_text += f"Postcured between {cure_results[3][0]} and {cure_results[3][-1]}"
        else:
            title_text += "Could not find postcure."

        if not (cure_results[0] and cure_results[2]):
            x_data = self.timeData
            y_data = self.temperatureData
            a.title.set_text(f'Time history for {self.name}, no cure cycle was detected')

        a.title.set_text(title_text)
        avg_window = 5
        # y_data = np.convolve(y_data, np.ones(avg_window)/avg_window, mode="valid")
        # x_data = x_data[:-avg_window+1]
        a.plot_date(x_data,
                    y_data,
                    'k-',
                    label=self.name,  # label
                    xdate=True)
        details_text = self._assemble_check_string(cure_results)
        left_limit = x_data[0] - dt.timedelta(minutes=1)
        right_limit = x_data[-1] + dt.timedelta(minutes=1)

        a.set_xlim(left_limit,
                   right_limit)

        out_graph_name = os.path.join(defaults.EXPORT_PATH,
                                      defaults.GRAPH_EXPORT_NAME.format(self.name,
                                                                        now.strftime(defaults.FNAME_TIME_FORMAT)))
        f.savefig(out_graph_name)
        self._write_to_box(msg_box, f'Output PNG to {out_graph_name}')

    def cure_cycle_check_corner_method(self):
        # go back in time and find each corner,
        # with a moving average of the max and min
        # document every time temp profile enters and leaves windows
        # considers success when an even list of times has a start and end time
        # longer than the required time.

        # algorithm is not that easy to understand but I think it's sound.
        # See the readme for a longer explanation.
        post_cured = False
        post_cure_entered = False
        post_cure_times = []  # an even numbered list of entry / exit times to the post_cure window
        cured = False
        cure_window_entered = False
        cure_window_times = []
        if (self.timeData[-1] - self.timeData[0]).total_seconds() < ccq.B_A:
            return [cured, cure_window_times, post_cured, post_cure_times]

        # df = pd.DataFrame({'Datetime': self.timeData, 'temperature': self.temperatureData})
        # df['Datetime'] = pd.to_datetime(df['Datetime'], format=defaults.DATETIME_FORMAT)
        # df = df.set_index(pd.DatetimeIndex(df['Datetime'])).bfill()

        i = len(self.temperatureData)

        while not post_cured:
            i -= 1
            if i < 0:
                i = len(self.temperatureData)
                break
            if ccq.postcure_bounds(self.temperatureData[i]) and not post_cure_entered:
                post_cure_entered = True
                post_cure_times.insert(0, self.timeData[i])

            if not ccq.postcure_bounds(self.temperatureData[i]) and post_cure_entered:
                post_cure_entered = False
                post_cure_times.insert(0, self.timeData[i+1])

            if len(post_cure_times) % 2 == 0 and post_cure_times:
                if (post_cure_times[-1] - post_cure_times[0]).total_seconds() > ccq.D_C:
                    post_cured = True
            elif len(post_cure_times) % 2 == 0 and post_cure_times and \
                    (post_cure_times[-1] - post_cure_times[0]).total_seconds() > 1.05 * ccq.D_C:
                post_cured = False
                break

        while not cured:
            i -= 1
            if i < 0:
                break
            if ccq.cure_bounds(self.temperatureData[i]) and not cure_window_entered:
                cure_window_entered = True
                cure_window_times.insert(0, self.timeData[i])

            if not ccq.cure_bounds(self.temperatureData[i]) and cure_window_entered:
                cure_window_entered = False
                cure_window_times.insert(0, self.timeData[i+1])

            if len(cure_window_times) % 2 == 0 and cure_window_times and \
                    (cure_window_times[-1] - cure_window_times[0]).total_seconds() > ccq.B_A:
                cured = True
            elif len(cure_window_times) % 2 == 0 and cure_window_times and \
                    (cure_window_times[-1] - cure_window_times[0]).total_seconds() > ccq.B_A:
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
