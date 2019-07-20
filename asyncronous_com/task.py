import time


class Task:

    def __init__(self):
        pass

    def __call__(self, instructions):
        result = 0
        for instruction in instructions:
            sections = instruction.split(':')
            time.sleep(float(sections[-1]))
            result += int(sections[0])
        return result
