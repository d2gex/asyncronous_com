import pytest
import time

from asyncronous_com.worker import Worker
from unittest.mock import patch, Mock, MagicMock
from pymulproc import factory, queuepi, mpq_protocol


@pytest.fixture(scope='module', autouse=True)
def tear_up_mock_producer():
    '''To avoid having to instantiate the producer socket
    '''
    with patch('asyncronous_com.worker.Producer'):
        yield


PARENT_ID = 1
WORKER_PID = 2
OTHER_WORKER_ID = 3


@pytest.fixture(scope='module')
def queue_factory():
    return factory.QueueCommunication()


@pytest.fixture(scope='module')
def app():
    return Mock()


@pytest.fixture(autouse=True)
def worker(queue_factory, app):
    worker = Worker('identity', 'url', queue_factory.child(), PARENT_ID, app)
    worker.parent_id = PARENT_ID
    worker.pid = WORKER_PID
    return worker


def empty_queue(comm):
    sms = comm.receive(func=lambda x: True)  # pop the message from the queue and make it empty again
    time.sleep(0.1)
    assert comm.conn.empty()
    return sms


def test_fixtures(worker):
    assert worker.pid == WORKER_PID
    assert isinstance(worker.producer, MagicMock)
    assert isinstance(worker.conn, queuepi.Child)


def test_sms_addressee_and_die(queue_factory, worker, app):
    '''A message is addressed to a worker if and only:

    1) The message has its PID printed ont it
    2) No PID at all is provided
    3) Otherwise the worker isn't the addressee

    It also tests that when a worker actually gets a REQ_DIE request, it actually stops the loop
    '''

    parent_comm = queue_factory.parent()
    assert parent_comm.conn.empty()

    # (1)
    parent_comm.send(mpq_protocol.REQ_DIE, recipient_pid=WORKER_PID)
    time.sleep(0.1)  # Required because the JoinableQueue is initialised by another process
    assert not parent_comm.conn.empty()
    worker.run(loops=1)
    time.sleep(0.1)
    app.assert_not_called()
    assert parent_comm.conn.empty()

    # (2)
    parent_comm.send(mpq_protocol.REQ_DIE)
    time.sleep(0.1)
    assert not parent_comm.conn.empty()
    worker.run(loops=1)
    time.sleep(0.1)
    app.assert_not_called()
    assert parent_comm.conn.empty()

    # (3)
    empty_queue(parent_comm)
    parent_comm.send(mpq_protocol.REQ_DIE, recipient_pid=OTHER_WORKER_ID)
    time.sleep(0.1)
    assert not parent_comm.conn.empty()
    worker.run(loops=1)
    time.sleep(0.1)
    app.assert_not_called()
    assert not parent_comm.conn.empty()
    empty_queue(parent_comm)
    time.sleep(0.1)
    assert parent_comm.conn.empty()


def test_perform_task(queue_factory, worker, app):
    '''A messaged that is addressed to a worker and is not a poison pill is interpreted as doing a task
    '''

    parent_comm = queue_factory.parent()
    task_data = 'data'
    parent_comm.send(mpq_protocol.REQ_DO, data=task_data)
    task_result = 'result'
    time.sleep(0.1)
    assert not parent_comm.conn.empty()
    with patch.object(worker.producer, 'run') as mock_producer_run:
        with patch.object(worker, 'app', return_value=task_result) as mock_app:
            worker.run(loops=1)
    time.sleep(0.1)

    assert not parent_comm.conn.empty()  # Now the queue should contain the message of the worker
    mock_app.assert_called_once_with(task_data)  # The app that performs the task should have been called
    mock_producer_run.assert_called_once_with(task_result)  # The result of the task is sent to the other end
    sms = empty_queue(parent_comm)  # Worker informs the parent that the task is finished
    assert sms[mpq_protocol.S_PID_OFFSET - 1] == mpq_protocol.REQ_FINISHED
    assert sms[mpq_protocol.R_PID_OFFSET] == PARENT_ID
