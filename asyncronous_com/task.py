import time


class Task:

    def __init__(self):
        pass

    def __call__(self, instructions):
        result = 0
        for instruction in instructions:
            response, wait = instruction
            time.sleep(float(wait))
            result += int(response)
        return result
