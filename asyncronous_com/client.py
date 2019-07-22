import zmq
import uuid

from asyncronous_com.iprocess import IProcess
from asyncronous_com import protocol
from asyncronous_com.com.sink import Sink
from asyncronous_com.com.producer import Producer


class Client(IProcess):

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.results = []
        self.producer = None
        self.sink = None

    def init_producer(self, identity, url, linger=0):
        self.producer = Producer(identity=identity, url=url, linger=linger)

    def init_sink(self, identity, url, linger=0):
        self.sink = Sink(identity=identity, url=url, linger=linger, s_type=zmq.PULL)

    def run(self, loops=True):
        '''Send a list of tasks to the other end via a producer socket and poll via sink socket to get the results. Both
        sending and receiving are asynchronous and independent from each other. This method will end when
        the expected num results have been achieved, a JOB_COMPLETE response has been received or when the
        maximum amount of loops have been exhausted.

        :param loops: Maximum number of loops this method should run for
        '''

        stop = False
        num_tasks = len(self.tasks)
        num_results = 0
        while not stop and loops:
            # (1) any task to send?
            if self.tasks:
                request = [protocol.TASK, str(uuid.uuid4()), self.tasks.pop()]
                # Is our queue full and we are unable to send => DIE
                if not self.producer.run(request):
                    stop = True

            # (2) Perhaps any input from the other end?
            response = self.sink.run()
            if response:
                if response[0] == protocol.JOB_COMPLETE:  # Job completed? => DIE
                    stop = True
                elif response[0] == protocol.TASK_DONE:
                    num_results += 1
                    self.results.append(response[-1])
                    if not self.tasks and num_results == num_tasks:  # Achieved what we came for? => DIE
                        stop = True

            # (3) Do we have a finite mandate?
            if not stop and not isinstance(loops, bool):
                loops -= 1

    def clean(self):
        if self.sink:
            self.sink.clean()
        if self.producer:
            self.producer.clean()
