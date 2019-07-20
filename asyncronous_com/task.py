import time


class Task:

    def __init__(self):
        self.result = 0

    def __call__(self, instructions):
        for instruction in instructions:
            sections = instruction.split(':')
            time.sleep(float(sections[-1]))
            self.result += int(sections[0])
        return self.result
