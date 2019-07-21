import multiprocessing
import zmq

from asyncronous_com import protocol
from asyncronous_com.iprocess import IProcess
from asyncronous_com.worker import Worker
from asyncronous_com.task import Task
from asyncronous_com.com.sink import Sink
from pymulproc import factory, mpq_protocol

MIN_PROCESSES = 2
MAX_PROCESSES = multiprocessing.cpu_count() * 2


class Server(IProcess):

    def __init__(self, identity, url, remote_url, max_processes, ip_map, linger=0):

        super().__init__()
        self.remote_url = remote_url
        self.max_processes = max(MIN_PROCESSES, MAX_PROCESSES, max_processes)
        self.ip_map = ip_map  # this should be a hash table for O(1) lookups

        self.child_processes = []
        self.queue_factory = factory.QueueCommunication()
        self.conn = self.queue_factory.parent()
        self.pid = multiprocessing.current_process().pid
        self.sink = Sink(identity=identity, url=url, linger=linger, s_type=zmq.PULL)

    def to_instructions(self, task):
        '''Given a task, convert all commands associated to ip addresses in it to instructions
        :param task: list of strings with format <response_integer>:<wait>
        :return: list of tuples with format(<response_integer>, <wait>)
        '''
        if not task:
            return None
        instructions = []
        for item in task:
            address, command = item.split(':')
            try:
                instruction = self.ip_map[address][command]
            except KeyError:
                pass
            else:
                instructions.append((instruction[0], instruction[-1]))
        return None if not instructions else instructions

    def launch_worker(self, identity):
        worker = Worker(identity=identity,
                        url=self.remote_url,
                        conn=self.queue_factory.child(),
                        parent_id=self.pid,
                        app=Task())
        worker.run()

    def kill_all(self):
        '''Kill all workers by sending them all a poison pill and wait until the confirm so
        '''
        for _ in range(len(self.child_processes)):
            self.conn.send(mpq_protocol.REQ_DIE)
        for child in self.child_processes:
            child.join()
        self.child_processes = []

    def run(self, loops=True):

        stop = False
        while not stop and loops:
            task = self.sink.run()
            if task:
                if task[0] == protocol.TASK:
                    instructions = self.to_instructions(task[-1])
                    # print(task[-1], instructions)
                    if instructions:
                        self.conn.send(mpq_protocol.REQ_DO, data=instructions)
                        if len(self.child_processes) < self.max_processes:
                            self.child_processes.append(
                                multiprocessing.Process(target=self.launch_worker,
                                                        args=(f'worker_{len(self.child_processes) + 1}',))
                            )
                            self.child_processes[-1].start()
                else:
                    self.kill_all()
            if not stop and not isinstance(loops, bool):
                loops -= 1

    def clean(self):
        self.kill_all()
        if self.sink:
            self.sink.clean()
