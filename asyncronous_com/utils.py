import re


def parse_line(line, server=True):
    '''Parse a provided string to ensure it is compliant with an command format
    '''
    sections = line.split(':')
    if server and len(sections) != 4:
        return None
    if not server and len(sections) != 2:
        return None
    if re.match(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}'
                          r'([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', sections[0]) is None:
        return None
    if sections[1] not in ('foo', 'bar'):
        return None
    if server:
        try:
            int(sections[2])
        except ValueError:
            return None
        try:
            float(sections[3])
        except ValueError:
            return None
    return line


def client_group_tasks(filename, block_size):
    '''Read a file and parse all lines, discarding those that do not conform with a command format and grouping
    them into block_size blocks.
    '''

    count = 1
    commands = []
    with open(filename) as fh:
        for line in fh:
            if parse_line(line, server=False):
                if count % block_size == 1 or block_size == 1:
                    commands.append([line])
                else:
                    commands[-1].append(line)
                count += 1
    return commands


def server_data_to_hash_table(filename):
    tasks = {}
    with open(filename, 'r') as fh:
        for line in fh:
            if parse_line(line):
                address, command, response, wait = line.split(':')
                try:
                    data = tasks[address]
                except KeyError:
                    tasks[address] = {command: (int(response), float(wait))}
                else:
                    data[command] = (int(response), float(wait))
                    tasks[address] = data
    return tasks
