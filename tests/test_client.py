import time
import pytest

from asyncronous_com.client import protocol, Client
from unittest.mock import patch, call
from tests import utils as test_utils


class TaskListStub:
    '''Stub that will emulate the client sending tasks to the server
    '''

    def __init__(self):
        self.task = ['instruction x', 'instruction x', 'instruction x']

    def pop(self):
        return self.task.pop()

    def __len__(self):
        return len(self.task)


@pytest.fixture(autouse=True)
def client():
    return Client(TaskListStub())


def test_initialisation_clean(client):

    client.init_sink(identity='client_sink', url=test_utils.TCP_BIND_URL_SOCKET)
    client.init_producer(identity='client_producer', url=test_utils.TCP_CONNECT_URL_SOCKET)
    time.sleep(0.1)

    assert not client.sink.socket.closed
    assert not client.producer.socket.closed
    time.sleep(0.1)

    client.clean()
    time.sleep(0.1)
    assert client.sink.socket.closed
    assert client.producer.socket.closed


def test_run_finite_loops(client):
    client.tasks = []  # Ensure that no tasks are processed to avoid hitting a stop=True
    loops = 10
    with patch.object(client, 'sink') as mock_sink:  # Ensure no responses are digested to avoid hitting stop=True
        mock_sink.run.return_value = False
        client.run(loops=loops)
    assert mock_sink.run.call_count == loops


def test_unable_to_send_and_die(client):
    '''When the client can't send anything to the other end it should die
    '''

    client.init_sink(identity='client_sink', url=test_utils.TCP_BIND_URL_SOCKET)
    client.init_producer(identity='client_producer', url=test_utils.TCP_CONNECT_URL_SOCKET)

    try:
        uuid4_value = '1'
        with patch('uuid.uuid4', return_value=uuid4_value):
            with patch.object(client.producer, 'run', return_value=False) as mock_producer_run:
                with patch.object(client.sink, 'run', return_value=False) as mock_sink_run:
                    with patch.object(client.tasks, 'pop', return_value=protocol.TASK):
                        client.run()

        mock_producer_run.assert_called_once_with([protocol.TASK, uuid4_value, protocol.TASK])
        assert mock_sink_run.call_count == 1
    finally:
        client.clean()  # No lose ends


def test_send_and_receive_tasks(client):
    '''The client sends a task and:

    1) Send a Task
    2) Receive Task Done
    3) Receive Job Complete
    '''

    client.init_sink(identity='client_sink', url=test_utils.TCP_BIND_URL_SOCKET)
    client.init_producer(identity='client_producer', url=test_utils.TCP_CONNECT_URL_SOCKET)

    try:
        # (1) and (2)
        uuid4_value = '1'
        task = 'instruction x'  # task sent to the other side
        msg_receive = [protocol.TASK_DONE, uuid4_value, task]  # msg supposed to be received
        assert not len(client.results)

        with patch('uuid.uuid4', return_value=uuid4_value):
            with patch.object(client.producer, 'run', return_value=True) as mock_producer_run:
                with patch.object(client.sink, 'run', return_value=msg_receive) \
                        as mock_sink_run:
                    with patch.object(client, 'tasks', TaskListStub()):
                        client.run()

        assert mock_producer_run.call_count == 3
        assert all(_call == call([protocol.TASK, uuid4_value, task]) for _call in mock_producer_run.call_args_list)
        assert mock_sink_run.call_count == 3
        assert len(client.results) == 3  # if TASK_DONE received => number of results is increased by one

        # (3)
        msg_receive[0] = protocol.JOB_COMPLETE
        with patch('uuid.uuid4', return_value=uuid4_value):
            with patch.object(client.producer, 'run', return_value=True) as mock_producer_run:
                with patch.object(client.sink, 'run', return_value=msg_receive) \
                        as mock_sink_run:
                    with patch.object(client, 'tasks', TaskListStub()):
                        client.run(loops=1)

        mock_producer_run.assert_called_once_with([protocol.TASK, uuid4_value, task])
        assert mock_sink_run.call_count == 1
        assert len(client.results) == 3  # Results does not change because JOB_COMPLETE does not affect it

    finally:
        client.clean()  # No lose ends
