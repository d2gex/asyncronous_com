import random

from os.path import join
from pathlib import Path

path = Path(__file__).resolve()
ROOT = path.parents[1]
TEST = join(ROOT, 'tests')

TCP_CLIENT_ADDRESS = "127.0.0.1"
TCP_SERVER_ADDRESS = "127.0.0.1"

TCP_PORT = "5556"
TCP_PROTOCOL = "tcp://"

TCP_CONNECT_URL_SOCKET = TCP_PROTOCOL + TCP_CLIENT_ADDRESS + ":" + TCP_PORT
TCP_BIND_URL_SOCKET = TCP_PROTOCOL + TCP_SERVER_ADDRESS + ":" + TCP_PORT


def generate_server_data(ip_address, max_num, response=(1, 3), wait=(1, 3)):
    '''Generate a list of commands associated to ip_addresses as well as the responses return per command and address
    and their waiting time
    '''
    data = []
    for item in range(max_num + 1):
        args = [ip_address,
                str(item),
                'foo',
                random.randint(*response) if isinstance(response, tuple) else response,
                random.randint(*wait) if isinstance(wait, tuple) else wait]
        data.append('{}_{}:{}:{}:{}'.format(*args))
        args[2] = 'bar'
        data.append('{}_{}:{}:{}:{}'.format(*args))
    return data
