=====================================================================================
``Asynchronous multiprocessing and multi-threading`` COM
=====================================================================================
**Note**: All tests have been run in a MacBook Pro i5 with dual cores.

This distributed software architecture that emulates a client-server system where the client sends batches of tasks to
the server for this to process and return the results back to the client. The approach uses a multiprocessing and
multi-threading version at the server side to overcome the CPython implementation problems with the GIL.

Description of the problem
===========================

The client will send a set of commands that the server would need to run remotely in other work stations within its
reach as provided by its network mask. Once the server has received a task, it will be passed on to a worker to perform
the remote command and obtained some results that will be directly sent over back to the client.

The remote commands will be emulated by sending the worker to sleep for an interval of period as provided in a hash
table that the server keeps in memory. When the client sends a task, the server will look for that task in the hash
table and will indicate the worker to sleep for as many seconds as indicated in the stored record associated to such
task.

The idea is to look for as much performance as possible, meaning that the client must not find impediments to send
tasks simultaneously and the server needs to digest them as soon as possible.

Solution
========
A socket-based asynchronous lightweight library such ZeroMQ has been used to design the solution. There are three main
processes that interact with each other as follows:

1.  **Client**: will use a a PUSH socket to send batches of tasks to the client and will be listening to a PULL sockets
    for results produced by the server, specifically from workers.
2.  **Server**: will be listening to a PULL socket for incoming tasks and will pass those into a shared queue with
    workers that will be picking a task each as they become available.
3.  **Worker**: will be using a PUSH socket to send all the results of applying the tasks received by the server process
    to the client. The worker is running a callable passing the received task which internally use multiple threads to
    maximise the responsiveness of the system.

The overall software architecture is represented by the diagrams below. The first diagram shows the multi-threading
nature of workers while the second provide further details about both type of queues used in the solution. The first
type is provided by ZeroMQ itself while the second is shared by both the server and worker processes, respectively.

.. image:: docs/images/multiprocessing_multithreading.png
    :alt: Multiprocessing and Multi-threading overall view
    :target: #

Multiprocessing and Multi-threading overall view

.. image:: docs/images/solution.png
    :alt: Asynchronous Multiprocessing solution
    :target: #

Details of the queues that make possible the task sharing and the concurrency on the task and result sending on
both directions

Final Notes
===========
**Both the sockets and processes have been developed using the template pattern while the workers are using the strategy
pattern to run the tasks provided by the server**. Workers are only mere vehicles to carry out tasks but they have no
understanding on what they are running as this could change at runtime - strategy pattern - at the server's will.


Install and Run
===============

Please download the repo and install the requirements as follow (create a virtual environment first):

.. code-block:: bash

    pip install -r requirements.txt

Then you can open two terminals so that you run the client side as:

.. code-block:: bash

    python -m asyncronous_com.run_client <<commands_file>> <<num_tasks_per_batch>> <<bind_url:port>> <<remote_url:port>>

    where:
    1.  *commands_file*: is the path to the file where lines of <<ip_address>>:<<command>> are stored for the client to
        send to the server. There is on file in 'tests/data/client_data.txt' that meets the requirements of the document
    2.  *num_tasks_per_batch*: Number of commands that can be sent at once per request to the server for maximum
        performance

An example of the client started on my local work station:

.. code-block:: bash

    python -m asyncronous_com.run_client tests/data/client_data.txt 16 tcp://127.0.0.1:5556 tcp://127.0.0.1:555

Then the server can be run as follows:

.. code-block:: bash

    python -m asyncronous_com.run_server  <<ip_map_file>> <<bind_url:port>> <<remote_url:port>> <<max_workers>>

    where:
    1.  *ip_map_file*: path to the file where the server will look for how long the command will run and what response
        will be returned. The file is converted to a Hash table for O(1) lookups.There is on file in
        'tests/data/server_data.txt' that meets the requirements of the document
    2.  *max_workers*: maximum number of workers that the server will create to serve all incoming requests.

An example of the server started on my remote work station:

.. code-block:: bash

    python -m asyncronous_com.run_server tests/data/server_data.txt tcp://127.0.0.1:5557 tcp://127.0.0.1:5556 32
