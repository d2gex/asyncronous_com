from tests import utils as test_utils


def test_generate_server_data():

    max_num = 3
    data = test_utils.generate_server_data('137.72.95', max_num, response=1, wait=1)
    assert len(data) == (max_num + 1) * 2
    for x in data:
        address, command, response, wait = x.split(':')
        assert all(x == '1' for x in (response, wait))

    max_num = 3
    data = test_utils.generate_server_data('137.72.95', max_num)
    assert len(data) == (max_num + 1) * 2
    for x in data:
        address, command, response, wait = x.split(':')
        assert all(1 <= int(x) <= 3 for x in (response, wait))
