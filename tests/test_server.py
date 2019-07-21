import pytest
import time
import multiprocessing

from pymulproc import factory, mpq_protocol
from asyncronous_com import protocol
from asyncronous_com.server import Server
from unittest.mock import patch
from tests import utils as test_utils


@pytest.fixture(scope='module')
def ip_map():
    return {
        '137.72.95.0': {
            'foo': (1, 1),
            'bar': (2, 2)
        },
        '137.72.95.1': {
            'foo': (1, 1),
            'bar': (2, 2)
        }
    }


@pytest.fixture(autouse=True)
def server(ip_map):
    _server = Server('identity',
                     test_utils.TCP_BIND_URL_SOCKET,
                     test_utils.TCP_CONNECT_URL_SOCKET,
                     4,
                     ip_map)
    return _server


def test_to_instructions(server):
    '''A task will be chopped up into instructions as follows:

    1) Nothing will be returned if the task given does not contain any ip address within our ip_map hash table
    2) Only those ip_addresses and commands within the task that match with our hash table will be converted to
    instructions
    '''

    # (1.1)
    task = []
    assert server.to_instructions(task) is None

    # (1.2)
    task = ['192.161.1.0:foo', '192.161.1.1:bar', '192.161.1.8:foo']
    assert server.to_instructions(task) is None

    # (2)
    task = ['137.72.95.0:foo', '137.72.95.1:bar', '137.72.95.0:bar',
            '137.72.95.1:foo', '137.72.95.1:no_command', '192.168.1.1:foo']
    instructions = server.to_instructions(task)
    assert [(1, 1), (2, 2), (2, 2), (1, 1)] == instructions


def test_launch_and_kill_workers(server):
    '''Create a bunch of workers and kill them all
    '''

    try:
        for offset in range(6):
            worker_process = multiprocessing.Process(target=server.launch_worker,
                                                     args=(f'worker_{offset}',))
            server.child_processes.append(worker_process)
            worker_process.start()

        for child in server.child_processes:
            assert child.pid and child.is_alive()
        child_processes = server.child_processes

        server.kill_all()

        for child in child_processes:
            assert not child.is_alive()
        assert not server.child_processes
    finally:
        server.clean()


def test_server_worker_conversation(server):
    '''The server will be picking up tasks from the other end via sink and adding them to the shared queue with
    its children as follows:

    1) if a 'TASK' task is picked, convert it to instructions and add it to the queue
        1.1) if no max_processes have been reached => create a worker
        1.2) Otherwise use existing workers
    2) if a 'JOB_COMPLETE' or 'JOB_ABORT' task is picked => kill all workers
    '''

    class SinkStub:
        '''Stub that will emulate the client sending tasks to the server
        '''

        def __init__(self):
            self.task = [
                [protocol.TASK, 1, ['137.72.95.0:foo']],
                [protocol.TASK, 2, ['137.72.95.0:bar']],
                [protocol.TASK, 3, ['137.72.95.1:foo']],
                [protocol.TASK, 4, ['137.72.95.1:bar']]
            ]

        def __call__(self):
            return self.task.pop()

        def __len__(self):
            return len(self.task)

    try:
        # (1.1)
        run = SinkStub()
        num_processes = len(run)
        with patch('time.sleep'):  # Avoid Task app to actually wait for each instruction
            with patch('asyncronous_com.worker.Producer.run') as mock_producer_run:  # No socket sending for worker
                with patch.object(server.sink, 'run', run):
                    server.run(loops=num_processes)
        assert not len(run)
        assert len(server.child_processes) == num_processes

        # (1.2)
        server.kill_all()
        assert not server.child_processes
        server.max_processes = 2
        run = SinkStub()
        loops = len(run)
        with patch('time.sleep'):
            with patch('asyncronous_com.worker.Producer.run') as mock_producer_run:
                with patch.object(server.sink, 'run', run):
                    server.run(loops=loops)
        assert not len(run)
        assert len(server.child_processes) == server.max_processes

        # (2)
        server.kill_all()
        assert not server.child_processes
        run = SinkStub()
        run.task = [[protocol.JOB_COMPLETE]] + run.task
        loops = len(run)
        with patch('time.sleep'):
            with patch('asyncronous_com.worker.Producer.run') as mock_producer_run:
                with patch.object(server.sink, 'run', run):
                    server.run(loops=loops)
        assert not len(run)
        assert not server.child_processes

    finally:
        server.clean()
        assert not server.child_processes
