from asyncronous_com import utils
from unittest.mock import patch


def test_parse_line():
    '''Ensure each line is parsed as follows:

    1) There are 4 sections separated by ':'
    2) First section is an IP Address
    3) Second section can only be 'foo' or 'bar'
    4) Third section is an integer
    5) Fourth section is either a float or an integer
    6) Otherwise return line as provided
    '''

    # (1)
    line = '4 sections :not found:'
    assert utils.parse_line(line) is None

    # (2)
    line = '192.168.1:command:response:wait'
    assert utils.parse_line(line) is None

    # (3)
    line = '192.168.1.0:command:response:wait'
    assert utils.parse_line(line) is None

    # (4)
    line = '192.168.1.0:foo:response:wait'
    assert utils.parse_line(line) is None

    # (5)
    line = '192.168.1.0:foo:9:wait'
    assert utils.parse_line(line) is None

    # (6.1)
    line = '192.168.1.0:foo:9:0.5'
    assert utils.parse_line(line) == line

    # (6.2)
    line = '192.168.1.0:bar:9:0.5'
    assert utils.parse_line(line) == line

    # (6.3)
    line = '192.168.1.0:bar:9:1'
    assert utils.parse_line(line) == line


def test_group_tasks():
    '''Ensure that group of instructions are formed as follows:

    1) malformed instructions are discarded
    2) Group of well-formed instructions are created
    '''
    file_data = [
            'This is not a well-formed instruction',
            '192.168.1.1:foo',
            '192.168.1.2:bar',
            '192.168.1.3:foo',
            '192.168.1.4:bar',
            '192.168.1.5:foo'
        ]
    with patch('builtins.open') as mock_fh:

        mock_fh.return_value.__enter__.return_value = file_data
        commands = utils.client_group_tasks('filename.txt', 2)
        assert len(commands) == 3
        assert all([instruction in file_data[1:]] for group in commands for instruction in group)
        assert file_data[0] not in commands

        commands = utils.client_group_tasks('filename.txt', 1)
        assert len(commands) == 5
        assert file_data[0] not in commands
        assert all([x in file_data] for x in commands)


def test_server_data_to_hash_table():
    '''Ensure that group of instructions are formed as follows:

    1) malformed instructions are discarded
    2) Group of well-formed instructions are created
    '''
    file_data = [
        'This is not a well-formed instruction',
        '192.168.1.1:foo:5:2',
        '192.168.1.1:bar:4:2.5',
        '192.168.1.3:foo:3:2',
        '192.168.1.3:bar:3:2',
        '192.168.1.4:foo:3:2.7'
    ]
    with patch('builtins.open') as mock_fh:

        mock_fh.return_value.__enter__.return_value = file_data
        instructions = utils.server_data_to_hash_table('filename.txt')
        assert len(instructions) == 3
        assert instructions['192.168.1.1']['foo'] == (5, 2)
        assert instructions['192.168.1.1']['bar'] == (4, 2.5)
        assert instructions['192.168.1.3']['foo'] == (3, 2)
        assert instructions['192.168.1.3']['bar'] == (3, 2)
        assert instructions['192.168.1.4']['foo'] == (3, 2.7)