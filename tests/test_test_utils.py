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
        x, y, z, w = address.split('.')
        assert int(x) == 137
        assert int(y) == 72
        assert int(z) == 95
        assert 0 <= int(w) <= 3
        assert all(1 <= int(x) <= 3 for x in (response, wait))


def test_generate_client_data():

    max_num = 3
    data = test_utils.generate_client_data('137.72.95', max_num)
    assert len(data) == (max_num + 1) * 2
    for x in data:
        address, command = x.split(':')
        x, y, z, w = address.split('.')
        assert int(x) == 137
        assert int(y) == 72
        assert int(z) == 95
        assert 0 <= int(w) <= 3
        assert command in ('foo', 'bar')
