Frequently Asked Questions
==========================

Can I use Mode with Django/Flask/etc.?
--------------------------------------

Yes! Use gevent/eventlet as a bridge to integrate with asyncio.

Using ``gevent``
~~~~~~~~~~~~~~~~

This works with any blocking Python library that can work with gevent.

Using gevent requires you to install the ``aiogevent`` module,
and you can install this as a bundle with Mode:

.. code-block:: console

    $ pip install -U mode[gevent]

Then to actually use gevent as the event loop you have to
execute the following in your entrypoint module (usually where you
start the worker), before any other third party libraries are imported::

    #!/usr/bin/env python3
    import mode.loop
    mode.loop.use('gevent')
    # execute program

REMEMBER: This must be located at the very top of the module,
in such a way that it executes before you import other libraries.


Using ``eventlet``
~~~~~~~~~~~~~~~~~~

This works with any blocking Python library that can work with eventlet.

Using eventlet requires you to install the ``aioeventlet`` module,
and you can install this as a bundle with Mode:

.. code-block:: console

    $ pip install -U mode[eventlet]

Then to actually use eventlet as the event loop you have to
execute the following in your entrypoint module (usually where you
start the worker), before any other third party libraries are imported::

    #!/usr/bin/env python3
    import mode.loop
    mode.loop.use('eventlet')
    # execute program

REMEMBER: It's very important this is at the very top of the module,
and that it executes before you import libraries.

Can I use Mode with Tornado?
----------------------------

Yes! Use the ``tornado.platform.asyncio`` bridge:
http://www.tornadoweb.org/en/stable/asyncio.html

Can I use Mode with Twisted?
-----------------------------

Yes! Use the asyncio reactor implementation:
https://twistedmatrix.com/documents/17.1.0/api/twisted.internet.asyncioreactor.html

Will you support Python 3.5 or earlier?
---------------------------------------

There are no immediate plans to support Python 3.5, but you are welcome to
contribute to the project.

Here are some of the steps required to accomplish this:

- Source code transformation to rewrite variable annotations to comments

  for example, the code::

        class Point:
            x: int = 0
            y: int = 0

   must be rewritten into::

        class Point:
            x = 0  # type: int
            y = 0  # type: int

- Source code transformation to rewrite async functions

    for example, the code::

        async def foo():
            await asyncio.sleep(1.0)

    must be rewritten into::

        @coroutine
        def foo():
            yield from asyncio.sleep(1.0)

Will you support Python 2?
--------------------------

There are no plans to support Python 2, but you are welcome to contribute to
the project (details in question above is relevant also for Python 2).


At Shutdown I get lots of warnings, what is this about?
-------------------------------------------------------

If you get warnings such as this at shutdown:

.. code-block:: text

    Task was destroyed but it is pending!
    task: <Task pending coro=<Service._execute_task() running at /opt/devel/mode/mode/services.py:643> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x1100a7468>()]>>
    Task was destroyed but it is pending!
    task: <Task pending coro=<Service._execute_task() running at /opt/devel/mode/mode/services.py:643> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x1100a72e8>()]>>
    Task was destroyed but it is pending!
    task: <Task pending coro=<Service._execute_task() running at /opt/devel/mode/mode/services.py:643> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x1100a7678>()]>>
    Task was destroyed but it is pending!
    task: <Task pending coro=<Event.wait() running at /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/asyncio/locks.py:269> cb=[_release_waiter(<Future pendi...1100a7468>()]>)() at /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/asyncio/tasks.py:316]>
    Task was destroyed but it is pending!
        task: <Task pending coro=<Event.wait() running at /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/asyncio/locks.py:269> cb=[_release_waiter(<Future pendi...1100a7678>()]>)() at /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/asyncio/tasks.py:316]>

It usually means you forgot to stop a service before the process exited.
