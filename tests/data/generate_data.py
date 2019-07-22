from os.path import join
from tests import utils as test_utils


if __name__ == "__main__":
    path = join(test_utils.TEST, 'data')
    with open(join(path, 'server_data.txt'), 'w+') as fh:
        for item in test_utils.generate_server_data('137.72.95', 255, response=1, wait=1):
            fh.write(item + '\n')

    with open(join(path, 'client_data.txt'), 'w+') as fh:
        for item in test_utils.generate_client_data('137.72.95', 255):
            fh.write(item + '\n')
