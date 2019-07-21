import multiprocessing
from pymulproc import mpq_protocol

from asyncronous_com.com.producer import Producer


class Worker:

    def __init__(self, identity, url, conn, parent_id, app, linger=0):
        self.pid = multiprocessing.current_process().pid
        self.parent_id = parent_id
        self.conn = conn
        self.app = app
        self.producer = Producer(identity=identity, url=url, linger=linger)

    def run(self, loops=True):

        stop = False
        while not stop and loops:

            # (1) is the task addressed to me?
            task = self.conn.receive(func=lambda sms: sms[mpq_protocol.R_PID_OFFSET] in (self.pid, None))
            if task:
                # (1.1) Is it a poison pill? => time pass away
                if task[mpq_protocol.S_PID_OFFSET - 1] == mpq_protocol.REQ_DIE:
                    stop = False
                # (1.2) Send the information via my producer and tell my parent that I am done with it
                else:
                    result = self.app(task[-1])
                    self.producer.run(result)
                    self.conn.send(mpq_protocol.REQ_FINISHED, recipient_pid=self.parent_id)

            # (2) Do we have a finite mandate?
            if not stop and not isinstance(loops, bool):
                loops -= 1
