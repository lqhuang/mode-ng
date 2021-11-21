=====================
AsyncIO Services Fork
=====================

|coverage| |license| |wheel| |pyversion| |pyimp|

:Version: 0.1.0
:Web: http://mode-ng.readthedocs.org/
:Download: https://pypi.org/project/mode-ng
:Source: https://github.com/lqhuang/mode-ng
:Keywords: async, service, framework, actors, bootsteps, graph


Why the fork
============

Original ``mode`` homepage: https://github.com/ask/mode. Thanks to its creator Ask Solem (@ask).

First fork: ``mode-streaming``
------------------------------

Project homepage: https://github.com/faust-streaming/mode-streaming

We have decided to fork the original *Mode* project because there is a critical process of releasing new versions which causes uncertainty in the community. Everybody is welcome to contribute to this *fork*, and you can be added as a manitainer.

We want to:

- Ensure continues release
- Code quality
- Support latest Python versions
- Update the documentation

and more...

A new fork: ``mode-ng``
-----------------------

**WIP** notice. Welcome to try it in your programs and feedback!

Well, here is an another fork for ``mode``. Generally, my target is to
create an individual and separated repository to develop ``mode`` for next
stage/generation and keep rolling forward fastly.

``mode`` could be a very potential and powerful framework for various
applications. So I very care about how ``faust-streaming`` and ``mode-streaming``
goes in future. Currently the most important thing in developing ``mode-streaming``
is to fix bugs and keep back compatibility for ``faust-streaming``, it would be
uncertain or not-willing to add new features. For now, one big problem is if I
try to continue working on current ``mode-streaming`` branch, it's hard to me
to know its consequences in ``faust-streaming``. I don't want to introduce
break changes and inconsistent behaviors.

Hence, ``mode-ng`` provides a new package to make some aggressive improvements, do some experiments,
and do not consider compatible problems from ``faust-streaming``. At least,
``mode-ng`` can be quickly used by more users with more advanced features to
build their own applications. In the future, if this fork could be ported back
to ``mode-streaming`` or used as base framework of ``faust-streaming``, that
would be really great!

Here are some thoughts from practical experiences and what I want to do next step:

- Bug fixes: yeah, why not.
- Use standard library implementations: When mode was first developed,
  many features haven't exist, so there are many hacks and tricky solutions in
  ``mode`` codes. Like ``cached_property``, ``AsyncMock``, ``loop arguments``,
  even ``Object`` class (missing some inner __xxx__ attrs after redefinition).
- Port some features from faust: ``web`` module in faust is really useful for
  building application. With web part, ``mode`` is able to expose, control,
  monitor and more from outside api.
- Improve or complete left part of ``signal`` module: Some modules like ``Signal``
  are unfinished. It will be useful for some observer patterns in programming.
- Add some message commuting behaviors like real actors? (for thread serices?)
- More documents and more examples

Why minimal supported Python version is ``3.10``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's more like a personal flavor for now. But if we say `py3.6` bring us stable ``async/await`` syntax firstly to introduce wonderful coroutine concurrency, I thought `py3.10` would be the next major popular minimal supported version with a more matured `asyncio` api interfaces. From feedbacks from many real cases, ``asyncio`` interfaces have changed a lot. Happy news is it stabilized by development of std library. And Python 3.10 is faster than before, though Python is not a language which cares about speed, seldom people don't want to higher performance.

This is not absolute, it aslo depends how many people want back compatibility for older versions.

What is Mode?
=============

Mode is a very minimal Python library built-on top of AsyncIO that makes
it much easier to use.

In Mode your program is built out of services that you can start, stop,
restart and supervise.

A service is just a class:

.. code:: python

    class PageViewCache(Service):
        redis: Redis = None

        async def on_start(self) -> None:
            self.redis = connect_to_redis()

        async def update(self, url: str, n: int = 1) -> int:
            return await self.redis.incr(url, n)

        async def get(self, url: str) -> int:
            return await self.redis.get(url)


Services are started, stopped and restarted and have
callbacks for those actions.

It can start another service:

.. code:: python

    class App(Service):
        page_view_cache: PageViewCache = None

        async def on_start(self) -> None:
            await self.add_runtime_dependency(self.page_view_cache)

        @cached_property
        def page_view_cache(self) -> PageViewCache:
            return PageViewCache()

It can include background tasks:

.. code:: python

    class PageViewCache(Service):

        @Service.timer(1.0)
        async def _update_cache(self) -> None:
            self.data = await cache.get('key')

Services that depends on other services actually form a graph
that you can visualize.

Worker
------

Mode optionally provides a worker that you can use to start the program,
with support for logging, blocking detection, remote debugging and more.

To start a worker add this to your program:

.. code:: python

    if __name__ == "__main__":
        from mode import Worker
        Worker(Service(), loglevel="info").execute_from_commandline()

Then execute your program to start the worker:

.. code:: console

    $ python examples/tutorial.py
    [2018-03-27 15:47:12,159: INFO]: [^Worker]: Starting...
    [2018-03-27 15:47:12,160: INFO]: [^-AppService]: Starting...
    [2018-03-27 15:47:12,160: INFO]: [^--Websockets]: Starting...
    STARTING WEBSOCKET SERVER
    [2018-03-27 15:47:12,161: INFO]: [^--UserCache]: Starting...
    [2018-03-27 15:47:12,161: INFO]: [^--Webserver]: Starting...
    [2018-03-27 15:47:12,164: INFO]: [^--Webserver]: Serving on port 8000
    REMOVING EXPIRED USERS
    REMOVING EXPIRED USERS

To stop it hit ``Control-c``:

.. code:: console

    [2018-03-27 15:55:08,084: INFO]: [^Worker]: Stopping on signal received...
    [2018-03-27 15:55:08,084: INFO]: [^Worker]: Stopping...
    [2018-03-27 15:55:08,084: INFO]: [^-AppService]: Stopping...
    [2018-03-27 15:55:08,084: INFO]: [^--UserCache]: Stopping...
    REMOVING EXPIRED USERS
    [2018-03-27 15:55:08,085: INFO]: [^Worker]: Gathering service tasks...
    [2018-03-27 15:55:08,085: INFO]: [^--UserCache]: -Stopped!
    [2018-03-27 15:55:08,085: INFO]: [^--Webserver]: Stopping...
    [2018-03-27 15:55:08,085: INFO]: [^Worker]: Gathering all futures...
    [2018-03-27 15:55:08,085: INFO]: [^--Webserver]: Closing server
    [2018-03-27 15:55:08,086: INFO]: [^--Webserver]: Waiting for server to close handle
    [2018-03-27 15:55:08,086: INFO]: [^--Webserver]: Shutting down web application
    [2018-03-27 15:55:08,086: INFO]: [^--Webserver]: Waiting for handler to shut down
    [2018-03-27 15:55:08,086: INFO]: [^--Webserver]: Cleanup
    [2018-03-27 15:55:08,086: INFO]: [^--Webserver]: -Stopped!
    [2018-03-27 15:55:08,086: INFO]: [^--Websockets]: Stopping...
    [2018-03-27 15:55:08,086: INFO]: [^--Websockets]: -Stopped!
    [2018-03-27 15:55:08,087: INFO]: [^-AppService]: -Stopped!
    [2018-03-27 15:55:08,087: INFO]: [^Worker]: -Stopped!

Beacons
-------

The ``beacon`` object that we pass to services keeps track of the services
in a graph.

They are not stricly required, but can be used to visualize a running
system, for example we can render it as a pretty graph.

This requires you to have the ``pydot`` library and GraphViz
installed:

.. code:: console

    $ pip install pydot

Let's change the app service class to dump the graph to an image at startup:

.. code:: python

    class AppService(Service):

        async def on_start(self) -> None:
            print('APP STARTING')
            import pydot
            import io

            o = io.StringIO()
            beacon = self.app.beacon.root or self.app.beacon
            beacon.as_graph().to_dot(o)
            graph, = pydot.graph_from_dot_data(o.getvalue())

            print('WRITING GRAPH TO image.png')
            with open('image.png', 'wb') as fh:
                fh.write(graph.create_png())


Creating a Service
==================

To define a service, simply subclass and fill in the methods
to do stuff as the service is started/stopped etc.:

.. code:: python

    class MyService(Service):

        async def on_start(self) -> None:
            print('Im starting now')

        async def on_started(self) -> None:
            print('Im ready')

        async def on_stop(self) -> None:
            print('Im stopping now')

To start the service, call ``await service.start()``:

.. code:: python

    await service.start()

Or you can use ``mode.Worker`` (or a subclass of this) to start your
services-based asyncio program from the console:

.. code:: python

    if __name__ == '__main__':
        import mode
        worker = mode.Worker(
            MyService(),
            loglevel='INFO',
            logfile=None,
            daemon=False,
        )
        worker.execute_from_commandline()

It's a Graph!
=============

Services can start other services, coroutines, and background tasks.

1) Starting other services using ``add_depenency``:

.. code:: python

    class MyService(Service):

        def __post_init__(self) -> None:
           self.add_dependency(OtherService(loop=self.loop))

2) Start a list of services using ``on_init_dependencies``:

.. code:: python

    class MyService(Service):

        def on_init_dependencies(self) -> None:
            return [
                ServiceA(loop=self.loop),
                ServiceB(loop=self.loop),
                ServiceC(loop=self.loop),
            ]

3) Start a future/coroutine (that will be waited on to complete on stop):

.. code:: python

    class MyService(Service):

        async def on_start(self) -> None:
            self.add_future(self.my_coro())

        async def my_coro(self) -> None:
            print('Executing coroutine')

4) Start a background task:

.. code:: python

    class MyService(Service):

        @Service.task
        async def _my_coro(self) -> None:
            print('Executing coroutine')


5) Start a background task that keeps running:

.. code:: python

    class MyService(Service):

        @Service.task
        async def _my_coro(self) -> None:
            while not self.should_stop:
                # NOTE: self.sleep will wait for one second, or
                #       until service stopped/crashed.
                await self.sleep(1.0)
                print('Background thread waking up')

.. _installation:

Installation
============

You can install Mode either via the Python Package Index (PyPI)
or from source.

To install using ``pip``:

.. code:: console

    $ pip install -U mode-ng

.. _installing-from-source:

Downloading and installing from source
--------------------------------------

Download the latest version of Mode from
http://pypi.org/project/mode-ng

You can install it by doing the following:

.. code:: console

    $ tar xvfz mode-ng-0.1.0.tar.gz
    $ cd mode-0.1.0
    $ python setup.py build
    # python setup.py install

The last command must be executed as a privileged user if
you are not currently using a virtualenv.

.. _installing-from-git:

Using the development version
-----------------------------

With pip
~~~~~~~~

You can install the latest snapshot of Mode using the following
pip command:

.. code:: console

    $ pip install https://github.com/lqhuang/mode-ng/zipball/master#egg=mode-ng

FAQ
===

Can I use Mode with Django/Flask/etc.?
--------------------------------------

Yes! Use gevent/eventlet as a bridge to integrate with asyncio.

Using ``gevent``
~~~~~~~~~~~~~~~~

This works with any blocking Python library that can work with gevent.

Using gevent requires you to install the ``aiogevent`` module,
and you can install this as a bundle with Mode:

.. code:: console

    $ pip install -U mode-ng[gevent]

Then to actually use gevent as the event loop you have to
execute the following in your entrypoint module (usually where you
start the worker), before any other third party libraries are imported:

.. code:: console

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

.. code:: console

    $ pip install -U mode-ng[eventlet]

Then to actually use eventlet as the event loop you have to
execute the following in your entrypoint module (usually where you
start the worker), before any other third party libraries are imported:

.. code:: console

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

At Shutdown I get lots of warnings, what is this about?
-------------------------------------------------------

If you get warnings such as this at shutdown:

.. code:: text

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

Code of Conduct
===============

Everyone interacting in the project's codebases, issue trackers, chat rooms,
and mailing lists is expected to follow the Mode Code of Conduct.

As contributors and maintainers of these projects, and in the interest of fostering
an open and welcoming community, we pledge to respect all people who contribute
through reporting issues, posting feature requests, updating documentation,
submitting pull requests or patches, and other activities.

We are committed to making participation in these projects a harassment-free
experience for everyone, regardless of level of experience, gender,
gender identity and expression, sexual orientation, disability,
personal appearance, body size, race, ethnicity, age,
religion, or nationality.

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery
* Personal attacks
* Trolling or insulting/derogatory comments
* Public or private harassment
* Publishing other's private information, such as physical
  or electronic addresses, without explicit permission
* Other unethical or unprofessional conduct.

Project maintainers have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct. By adopting this Code of Conduct,
project maintainers commit themselves to fairly and consistently applying
these principles to every aspect of managing this project. Project maintainers
who do not follow or enforce the Code of Conduct may be permanently removed from
the project team.

This code of conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community.

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by opening an issue or contacting one or more of the project maintainers.

This Code of Conduct is adapted from the Contributor Covenant,
version 1.2.0 available at http://contributor-covenant.org/version/1/2/0/.


.. |coverage| image:: https://codecov.io/github/lqhuang/mode-ng/coverage.svg?branch=master
    :target: https://codecov.io/github/lqhuang/mode-ng?branch=master

.. |license| image:: https://img.shields.io/pypi/l/mode-ng.svg
    :alt: BSD License
    :target: https://opensource.org/licenses/BSD-3-Clause

.. |wheel| image:: https://img.shields.io/pypi/wheel/mode-ng.svg
    :alt: Mode can be installed via wheel
    :target: http://pypi.org/project/mode-ng/

.. |pyversion| image:: https://img.shields.io/pypi/pyversions/mode-ng.svg
    :alt: Supported Python versions.
    :target: http://pypi.org/project/mode-ng/

.. |pyimp| image:: https://img.shields.io/pypi/implementation/mode-ng.svg
    :alt: Supported Python implementations.
    :target: http://pypi.org/project/mode-ng/
