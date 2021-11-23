import requests
from lxml import html


def read_temperature(address, credentials):
    address = 'https://' + address
    session_requests = requests.session()
    print(address)
    print(credentials)
    result = requests.get(address, auth=(credentials['user'], credentials['pwd']), timeout=None)
    print('Successfully fetched')
    print(result.text)

    tree = html.fromstring(result.text)
    # authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]


if __name__ == '__main__':
    read_temperature('www.bbc.co.uk', {'user': 'fact', 'pwd': '35$%LG!'})
    read_temperature('http://192.168.1.1/start.htm', {'user': 'admin', 'pwd': 'adminFACT8'})