import re


def parse_line(line):
    '''Parse a provided string to ensure it is compliant with an command format
    :param line: string
    '''
    sections = line.split(':')
    if len(sections) != 4:
        return None
    if re.match(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}'
                          r'([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', sections[0]) is None:
        return None
    if sections[1] not in ('foo', 'bar'):
        return None
    try:
        int(sections[2])
    except ValueError:
        return None
    try:
        float(sections[3])
    except ValueError:
        return None
    return line


def group(filename, block_size):
    '''Read a file and parse all lines, discarding those that do not conform with a command format and grouping
    them into block_size blocks.
    '''

    count = 1
    commands = []
    with open(filename) as fh:
        for line in fh:
            if parse_line(line):
                if count % block_size == 1 or block_size == 1:
                    commands.append([line])
                else:
                    commands[-1].append(line)
                count += 1
    return commands
