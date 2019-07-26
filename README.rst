=====================================================================================
``All-in-memory asynchronous multiprocessing and multi-threading`` client-server COM
=====================================================================================
**Note**: All tests have been run in a Macbook Pro i5 with dual cores.

Multi-threading with IO operations
===================================

This version of the software implements the originally envisaged solution using both multiprocessing and multi-threading
as mentioned in the 'master' branch.  In the section *Understanding the problem* I mentioned that the solution of this
problem would benefit from multi-threading given the amount of I/O operations that need to be carried out. That meant
that most of the time the processors would be idle and therefore available for another thread to execute.

With this new version of the software, the time of around ~ 17 seconds of the previous solution to solve 512 client
requests of 1 second waiting time is **much reduced to ~ 1.35 seconds - 17 times faster, when the client sends batches
of 16 tasks and 32 workers are run which will eventually create 512 threads**.

In the section *Multiprocessing vs Multi-threading* I also explained the problems of the GIL in Python. Unfortunately,
the CPython implementation of Python will not use the underlying 2 cores when using multi-threading *alone* given
the there is only one global mutually-exclusive lock per process running those threads. How can that be demonstrated?

a) Following the former example, an example when running only one process and 16 threads show that the time taken
to provide all results take approximately ~ 32.2 seconds. Doing the maths, each request takes 1 second and tasks are
digested in blocks of 16. The client is sending the tasks to the server asynchronously and almost instantaneously
given the proximity. Then each bach takes around 1.0.. seconds to be processed and all 16 threads are put to sleep.
In order to complete the 512 requests, 32 batches of 16 tasks need to be consumed so that makes it **32 x 1.0... = 32.2
seconds**.

But do we have two cores so two threads should have been run simultaneously within the CPU and concurrently within the
worker, reducing that time in half. Well here the GIL is restricting us.

b) The second example shows that when using two threads, meaning that to processes are run simultaneously and in turn
that a thread of process A and a thread of process B run two simultaneously within the CPU, the time taken is exactly
just half: ~16.11.

Multi-threading with CUP intensive tasks
========================================

The whole scenario changes when the tasks that each thread or process are given are computationally expensive.
This means that the CPU rather than being idle will be busy. There is no much benefit from running more than two
processed at the same time as only two processes can be run simultaneously within the two available cores.

In yet another test both versions of the software have been tested with 2 workers for tasks that take around 70
milliseconds each to complete - 2 million loops. The result of Multiprocessing-Multithreading vs Multiprocessing only
have very similar. The former takes ~ 15.05 seconds vs 16.62 seconds on the latter. There is no much point to use
many more processes as only two can be run at the same time. In fact when running both versions of the software with
up to 8 workers for Multiprocessing/Multithreading and up to 4 for Multiprocessing only the times are 13.84 vs 15.1
seconds. This could be because each loop don't always take 70 milliseconds but less, so statistically speaking there
are more possibilities to hit less time-consuming loops when the size of the sample is bigger. The fact that are
more sockets to send the results may also have some impact but at the end of the day this is cpu-time that needs to
be allocated each worker so...


The solution
============

The worker, client and server has not changed one bit. What has changed is the **Task class** itself where rather than
running a typical sequential loop multiple threads are given those tasks to be digested. The task class however has
been modified so that supports;

1.  I/O operations that are run sequentially for the Multiprocessing-only solution
2.  CPU-intensive operations for the Multiprocessing-only solution
3.  I/O operations that are run concurrently by all threads within a worker in the Multiprocessing-Multi-threading sol.
4.  CPU-intensive for Multiprocessing-Multi-threading sol

The architecture of the solution was intentionally designed so that the refactoring of the software to provide a second
version adding Multi-threading was easy to accomplished. The changes on the code can be seen here:

https://github.com/d2gex/asyncronous_com/compare/master...multithreading_version

**Lastly it is important to notice that threads only compute commands but do not interact with the sockets that are used
to communicate with the client. This is only done by the parent process to gain reliability and avoid complex scenarios.**

Conclusion
===========
At least in the CPython implementation of Python and given the GIL restriction, to get the best of Multi-threading some
Multi-processing will be needed so that multiple threads can run at the same time on the underlying cores, should the
work station be multi-core.

When the nature of the operations are I/O this solution works much better than Multiprocessing-only, because we are
increasing that responsiveness of the system that I mentioned in the version 1 of the software. Additionally and very
important too, it may increase reliability too as with just only 8 workers and therefore 8 sockets open, the performance
is increased by 4 regarding Multiprocessing-only and 32 workers - albeit the test shows that with 8 workers the
Multi-threading version takes around 4.1 seconds.


Remaining Question
==================
The question about how the client and server agree a configuration remains. As said previously another non-blocking
request-reply channel can be added to the software architecture. The idea is that the server would always be listen to
a ROUTER socket - reply - to exchange metadata with the client and agree how many tasks are going to be sent and agree
a configuration.

The beauty of ZeroMQ is that a DEALER-ROUTER configuration, allows request-reply in both directions and by adding
polling, many conversations can be held at the same time. This effectively means that a server can hold various
conversation with the different clients.


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
