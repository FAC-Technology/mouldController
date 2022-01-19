import queue

import requests
import socket
from . import defaults
from threading import Thread


def try_pwd(target, guess):
    try:
        response = requests.get(f"http://{target['location']}",
                                headers=defaults.headers,
                                cookies=defaults.cookies,
                                auth=(target['user'], guess),
                                verify=False,
                                timeout=1)
        if response.status_code == 200:
            return True
        else:
            return False
    except (requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout):
        defaults.log.warning(msg=f"{target['name']} timed out over a second")
    except requests.exceptions.ConnectionError:
        return False


class Hunter:
    def __init__(self):
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _s.connect(("8.8.8.8", 80))
        _full_ip = _s.getsockname()[0]
        _s.close()
        self._ip_prefix = '.'.join(_full_ip.split('.')[:-1]) + '.'
        self.nds = []
        self.found_count = 0
        self.dac_count = 8
        self._pwd_list = [f'qqqqqqq{i+1}' for i in range(self.dac_count)]
        self.populate_list()

    def populate_list(self):
        self.find_nd_ips()
        self.pwd_test()
        for i, nd in enumerate(self.nds):
            if nd['name'] == '':
                self.nds.remove(nd)
        self.found_count = len(self.nds)

    def find_nd_ips(self):
        self.nds = []  # wipe nanodac list
        threads = []  # list of threads
        finds = []  # list of locations where ND identified
        que = queue.Queue()  # queue object to store
        for i in range(255):  # try every IP simultaneously
            threads.append(Thread(target=lambda q, arg1: q.put(self.ping_dac(arg1)), args=(que, i)))
            threads[-1].start()

        for t in threads:  # join the threads
            t.join()

        while not que.empty():  # go through the results
            result = que.get()
            if result is not None:
                finds.append(result)

        for suffix in finds:  # rebuild ND list
            self.nds.append({'location': f'{self._ip_prefix}{suffix}',
                             'name': '',
                             'user': 'admin',
                             'pwd': ''})

    def pwd_test(self):
        for i, nd in enumerate(self.nds):
            for j, pwd in enumerate(self._pwd_list):
                if try_pwd(nd, pwd):
                    self.nds[i]['name'] = f'dac_{j+1}'
                    self.nds[i]['pwd'] = pwd

    def ping_dac(self, i):
        try:
            response = requests.get(f'http://{self._ip_prefix}{i}',
                                    headers=defaults.headers,
                                    cookies=defaults.cookies,
                                    verify=False,
                                    timeout=0.08)
            if 'www-authenticate' in response.headers.keys():
                if 'Eurotherm' in response.headers['www-authenticate']:
                    return i
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError):
            pass
