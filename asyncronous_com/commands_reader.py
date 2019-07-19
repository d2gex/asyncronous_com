import re


class CommandReader:

    def __init__(self, filename, block_size):
        ''''Initialise the Client parent process
        :param filename:
        :param block_size: number of lines of the give filename that will conform a single block
        '''
        self._commands = []
        self.filename = filename
        self.block_size = block_size

    @property
    def commands(self):
        return self._commands

    @staticmethod
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

    def group(self):
        '''Read a file and parse all lines, discarding those that do not conform with a command format and grouping
        them into block_size blocks.
        '''

        count = 1
        with open(self.filename) as fh:
            for line in fh:
                if self.parse_line(line):
                    if count % self.block_size == 1 or self.block_size == 1:
                        self._commands.append([line])
                    else:
                        self._commands[-1].append(line)
                    count += 1
