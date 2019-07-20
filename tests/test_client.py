import time

from asyncronous_com.client import protocol, Client
from unittest.mock import Mock, patch
from tests import utils as test_utils


def test_initialisation_clean():

    _client = Client(Mock())
    _client.init_sink(identity='client_sink', url=test_utils.TCP_BIND_URL_SOCKET)
    _client.init_producer(identity='client_producer', url=test_utils.TCP_CONNECT_URL_SOCKET)
    time.sleep(0.1)

    assert not _client.sink.socket.closed
    assert not _client.producer.socket.closed
    time.sleep(0.1)

    _client.clean()
    time.sleep(0.1)
    assert _client.sink.socket.closed
    assert _client.producer.socket.closed


def test_run_finite_loops():
    _client = Client(None)
    loops = 10
    with patch.object(_client, 'sink') as mock_sink:
        mock_sink.run.return_value = False
        _client.run(loops=loops)
    assert mock_sink.run.call_count == loops


def test_unable_to_send_and_die():
    '''When the client can't send anything to the other end it should die
    '''

    _client = Client(Mock())
    _client.init_sink(identity='client_sink', url=test_utils.TCP_BIND_URL_SOCKET)
    _client.init_producer(identity='client_producer', url=test_utils.TCP_CONNECT_URL_SOCKET)

    try:
        uuid4_value = '1'
        with patch('uuid.uuid4', return_value=uuid4_value):
            with patch.object(_client.producer, 'run', return_value=False) as mock_producer_run:
                with patch.object(_client.sink, 'run', return_value=False) as mock_sink_run:
                    with patch.object(_client.tasks, 'pop', return_value=protocol.TASK):
                        _client.run()

        mock_producer_run.assert_called_once_with([protocol.TASK, uuid4_value, protocol.TASK])
        assert mock_sink_run.call_count == 1
    finally:
        _client.clean()  # No lose ends


def test_send_and_receive_tasks():
    '''The client sends a task and:

    1) Send a Task
    2) Receive Task Done
    3) Receive Job Complete
    '''

    _client = Client(Mock())
    _client.init_sink(identity='client_sink', url=test_utils.TCP_BIND_URL_SOCKET)
    _client.init_producer(identity='client_producer', url=test_utils.TCP_CONNECT_URL_SOCKET)

    try:
        # (1) and (2)
        uuid4_value = '1'
        task = 'instruction x'  # task sent to the other side
        msg_receive = [protocol.TASK_DONE, uuid4_value, task]  # msg supposed to be received
        assert not len(_client.results)

        with patch('uuid.uuid4', return_value=uuid4_value):
            with patch.object(_client.producer, 'run', return_value=True) as mock_producer_run:
                with patch.object(_client.sink, 'run', return_value=msg_receive) \
                        as mock_sink_run:
                    with patch.object(_client.tasks, 'pop', return_value=task):
                        _client.run(loops=1)

        mock_producer_run.assert_called_once_with([protocol.TASK, uuid4_value, task])
        assert mock_sink_run.call_count == 1
        assert len(_client.results) == 1  # if TASK_DONE received => number of results is increased by one

        # (3)
        msg_receive[0] = protocol.JOB_COMPLETE
        with patch('uuid.uuid4', return_value=uuid4_value):
            with patch.object(_client.producer, 'run', return_value=True) as mock_producer_run:
                with patch.object(_client.sink, 'run', return_value=msg_receive) \
                        as mock_sink_run:
                    with patch.object(_client.tasks, 'pop', return_value=task):
                        _client.run(loops=1)

        mock_producer_run.assert_called_once_with([protocol.TASK, uuid4_value, task])
        assert mock_sink_run.call_count == 1
        assert len(_client.results) == 1  # Results does not change because JOB_COMPLETE does not affect it

    finally:
        _client.clean()  # No lose ends
