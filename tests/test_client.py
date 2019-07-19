from asyncronous_com.commands_reader import CommandReader
from unittest.mock import patch, MagicMock


def test_parse_line():
    '''Ensure each line is parsed as follows:

    1) There are 4 sections separated by ':'
    2) First section is an IP Address
    3) Second section can only be 'foo' or 'bar'
    4) Third section is an integer
    5) Fourth section is either a float or an integer
    6) Otherwise return line as provided
    '''
    comm_reader = CommandReader('filename.txt', 2)

    # (1)
    line = '4 sections :not found:'
    assert comm_reader.parse_line(line) is None

    # (2)
    line = '192.168.1:command:response:wait'
    assert comm_reader.parse_line(line) is None

    # (3)
    line = '192.168.1.0:command:response:wait'
    assert comm_reader.parse_line(line) is None

    # (4)
    line = '192.168.1.0:foo:response:wait'
    assert comm_reader.parse_line(line) is None

    # (5)
    line = '192.168.1.0:foo:9:wait'
    assert comm_reader.parse_line(line) is None

    # (6.1)
    line = '192.168.1.0:foo:9:0.5'
    assert comm_reader.parse_line(line) == line

    # (6.2)
    line = '192.168.1.0:bar:9:0.5'
    assert comm_reader.parse_line(line) == line

    # (6.3)
    line = '192.168.1.0:bar:9:1'
    assert comm_reader.parse_line(line) == line


def test_process():
    '''Ensure that group of instructions are formed as follows:

    1) malformed instructions are discarded
    2) Group of well-formed instructions are created
    '''
    comm_reader = CommandReader('filename.txt', 2)
    file_data = [
            'This is not a well-formed instruction',
            '192.168.1.1:foo:5:2',
            '192.168.1.2:bar:4:2.5',
            '192.168.1.3:foo:3:2',
            '192.168.1.4:bar:3:2',
            '192.168.1.5:foo:3:2.7'
        ]
    with patch('builtins.open') as mock_fh:

        mock_fh.return_value.__enter__.return_value = file_data
        comm_reader.group()
        assert len(comm_reader.commands) == 3
        assert all([instruction in file_data[1:]] for group in comm_reader.commands for instruction in group)
        assert file_data[0] not in comm_reader._commands

        comm_reader._commands = []
        comm_reader.block_size = 1
        comm_reader.group()
        assert len(comm_reader.commands) == 5
        assert file_data[0] not in comm_reader.commands
        assert all([x in file_data] for x in comm_reader.commands)
