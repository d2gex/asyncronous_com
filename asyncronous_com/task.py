import time
from collections import deque
from threading import Thread


class SingleProcessIOTask:

    def __init__(self):
        pass

    def __call__(self, instructions):
        result = 0
        for instruction in instructions:
            response, wait = instruction
            time.sleep(float(wait))
            result += int(response)
        return result


class SingleProcessCPUTask:

    def __init__(self):
        pass

    def __call__(self, instructions):
        result = 0
        for instruction in instructions:
            response, wait = instruction
            for _ in range(2000000):  # it takes roughly 70 milliseconds on a i% processor - 0.07 seconds
                pass
            result += int(response)
        return result


class ThreadTask:
    '''Implement a callable object that will run one thread per task provided. The results are all provided at once
    so that the parent process is the only one with access to the socket.
    '''

    def __init__(self):
        self.results = []
        super().__init__()

    @staticmethod
    def run_instruction(ins, queue):
        pass

    def __call__(self, instructions):

        results = deque()  # Thread-safe queue
        threads = []
        for instruction in instructions:
            threads.append(Thread(target=self.run_instruction, args=(instruction, results)))
            threads[-1].start()

        for offset in range(len(instructions)):
            threads[offset].join()

        return sum(results)


class ThreadIOTask(ThreadTask):

    def __init__(self):
        super().__init__()

    @staticmethod
    def run_instruction(ins, queue):
        '''Run one instruction at the time and add the result ot the thread-safe queue
               '''
        response, wait = ins
        time.sleep(float(wait))
        queue.append(int(response))


class ThreadCPUTask(ThreadTask):
    @staticmethod
    def run_instruction(ins, queue):
        '''Run one instruction at the time and add the result ot the thread-safe queue
               '''
        response, wait = ins
        for _ in range(2000000):  # it takes roughly 70 milliseconds on a i% processor - 0.07 seconds
            pass
        queue.append(int(response))
