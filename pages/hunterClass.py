import queue

import requests
import socket
from . import defaults
from threading import Thread
import time


def try_pwd(target, guess, old):
    # try once the old location and password for efficiency
    if old != 0 and old['pwd'] == guess:
        try:
            response = requests.get(f"http://{old['location']}",
                                    headers=defaults.headers,
                                    cookies=defaults.cookies,
                                    auth=(old['user'], old['pwd']),
                                    verify=False,
                                    timeout=1)
            if response.status_code == 200:
                print(f"Got {old['name']}pwd correct first time")
                return True
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout) as e:
            print(f'Struggling with trying pwds for reason of {e}')
            defaults.log.warning(msg=f"{target['name']} timed out over a second")
        except requests.exceptions.ConnectionError as e:
            print(f'Struggling with trying pwds for reason of {e}')
    print(f"Didn't get password right for {target['location']} right first time")
    try:
        response = requests.get(f"http://{target['location']}",
                                headers=defaults.headers,
                                cookies=defaults.cookies,
                                auth=(target['user'], guess),
                                verify=False,
                                timeout=1)
        if response.status_code == 200:
            return True
    except (requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout) as e:
        print(f'Struggling with trying pwds for reason of {e}')
        defaults.log.warning(msg=f"{target['name']} timed out over a second")
    except requests.exceptions.ConnectionError as e:
        print(f'Struggling with trying pwds for reason of {e}')
    return False


class Hunter:
    def __init__(self):
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _s.connect(("8.8.8.8", 80))
        _full_ip = _s.getsockname()[0]
        _s.close()
        self._ip_prefix = '.'.join(_full_ip.split('.')[:-1]) + '.'
        self.nds = []
        self.old_nds = []
        self.dac_count = 8
        self._pwd_list = [f'qqqqqqq{i+1}' for i in range(self.dac_count)]
        self.populate_list()

    def populate_list(self):  # function fills the nd list
        print('Hunting for nanodacs')
        t1 = time.time()
        self.find_nd_ips()
        t2 = time.time()
        if self.nds:
            self.pwd_test()
        print(f'\rFinding ips took {round((t2 - t1) * 1e3)}ms\n' +
              f'Password testing took {round((time.time() - t2) * 1e3)}ms\r')

        for nd in self.nds:  # if a location couldn't be found, ignore it
            if nd['name'] == '':
                self.nds.remove(nd)

    def find_nd_ips(self):
        self.old_nds = self.nds
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

        for suffix in finds:  # rebuild ND list without passwords or names
            self.nds.append({'location': f'{self._ip_prefix}{suffix}',
                             'name': '',
                             'user': 'admin',
                             'pwd': ''})

    def pwd_test(self):  # try every password in every nanodac until the correct is found
        # for old_nd in self.old_nds:
        #     if old_nd['name'] not in [name for name in self.nds]:
        #         self.old_nds.append(0)
        if not self.old_nds:
            self.old_nds += [0] * (len(self.nds)-len(self.old_nds))
        # if len(self.old_nds) != len(self.nds):
        #     self.old_nds += [0] * (len(self.nds)-len(self.old_nds))  # add zeros to non tried NDs

        for i, (nd, old) in enumerate(zip(self.nds, self.old_nds)):
            for j, pwd in enumerate(self._pwd_list):
                if try_pwd(nd, pwd, old):
                    self.nds[i]['name'] = f'dac {j+1}'
                    self.nds[i]['pwd'] = pwd
                    break

    def ping_dac(self, i):  # function to determine if the answer is from a Eurotherm nanodac
        try:
            response = requests.get(f'http://{self._ip_prefix}{i}',
                                    headers=defaults.headers,
                                    cookies=defaults.cookies,
                                    verify=False,
                                    timeout=0.12)
            if 'www-authenticate' in response.headers.keys():
                if 'Eurotherm' in response.headers['www-authenticate']:
                    return i
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError):
            pass
