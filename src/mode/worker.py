"""Worker - Starts services from the command-line.

Workers add signal handling, logging, and other things
required to start and manage services in a process environment.
"""
from __future__ import annotations

from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Iterable,
    Iterator,
    NoReturn,
    cast,
)

import asyncio
import logging as _logging
import os
import reprlib
import signal
import sys
import traceback
from asyncio import all_tasks
from contextlib import contextmanager, suppress
from logging import Handler, Logger

from .services import Service
from .types import ServiceT
from .utils import logging
from .utils.futures import maybe_cancel
from .utils.imports import symbol_by_name
from .utils.times import Seconds

if TYPE_CHECKING:
    from .debug import BlockingDetector
    from .utils.logging import Severity

__all__ = ["Worker"]

logger = logging.get_logger(__name__)

EX_OK = getattr(os, "EX_OK", 0)
EX_FAILURE = 1
EX_OSERR = getattr(os, "EX_OSERR", 71)
BLOCK_DETECTOR = "mode.debug:BlockingDetector"


class _TupleAsListRepr(reprlib.Repr):
    def repr_tuple(self, x: tuple, level: int) -> str:
        return self.repr_list(cast(list, x), level)


# this repr formats tuples as if they are lists.
_repr = _TupleAsListRepr().repr  # noqa: E305


@contextmanager
def exiting(*, print_exception: bool = False, file: IO = sys.stderr) -> Iterator[None]:
    try:
        yield
    except MemoryError:
        sys.stderr.write("Out of memory!")
        sys.exit(EX_OSERR)
    except Exception as exc:
        if print_exception:
            print(f"Command raised exception: {exc!r}", file=file)
            traceback.print_tb(exc.__traceback__, file=file)
        sys.exit(EX_FAILURE)
    sys.exit(EX_OK)


class Worker(Service):
    """Start mode service from the command-line."""

    BLOCK_DETECTOR: ClassVar[str] = BLOCK_DETECTOR

    debug: bool
    quiet: bool
    stdout: IO
    stderr: IO
    log_level: Severity | None
    log_file: str | os.PathLike | IO | None
    log_handlers: list[Handler]
    logging_config: dict | None
    redirect_stdouts: bool
    redirect_stdouts_level: int

    services: Iterable[ServiceT]

    console_port: int
    blocking_timeout: Seconds
    _blocking_detector: BlockingDetector | None = None
    _starting_fut: asyncio.Future | None = None

    # signals can be called multiple times,
    # so when stopped by signal we record the time to make sure
    # we don't start the process multiple times.
    _signal_stop_time: float | None = None
    _signal_stop_future: asyncio.Future | None = None

    def __init__(
        self,
        *services: ServiceT,
        debug: bool = False,
        quiet: bool = False,
        log_level: Severity = _logging.INFO,
        log_file: str | os.PathLike | IO | None = None,
        log_handlers: list[Handler] | None = None,
        redirect_stdouts: bool = True,
        redirect_stdouts_level: Severity = _logging.WARN,
        stdout: IO | None = sys.stdout,
        stderr: IO | None = sys.stderr,
        override_logging: bool = True,
        logging_config: dict | None = None,
        console_port: int = 50101,
        blocking_timeout: Seconds = 10.0,
        daemon: bool = True,
        loop: asyncio.AbstractEventLoop | None = None,
        **kwargs: Any,
    ) -> None:
        self.services = services
        self.debug = debug
        self.quiet = quiet

        self.log_level = log_level
        self.log_file = log_file
        self.log_handlers = log_handlers or []
        self.redirect_stdouts = redirect_stdouts
        self.redirect_stdouts_level = logging.level_number(redirect_stdouts_level)
        self.stdout = sys.stdout if stdout is None else stdout
        self.stderr = sys.stderr if stderr is None else stderr
        self.override_logging = override_logging
        self.logging_config = logging_config

        self.console_port = console_port
        self.blocking_timeout = blocking_timeout
        self.daemon = daemon
        super().__init__(loop=loop, **kwargs)

        if self.services:
            for service in self.services:
                service.beacon.reattach(self.beacon)
                assert service.beacon.root is self.beacon

    def say(self, msg: str) -> None:
        """Write message to standard out."""
        self._say(msg)

    def carp(self, msg: str) -> None:
        """Write warning to standard err."""
        self._say(msg, file=self.stderr)

    def _say(
        self, msg: str, file: IO | None = None, end: str = "\n", **kwargs: Any
    ) -> None:
        if file is None:
            file = self.stdout
        if not self.quiet:
            print(msg, file=file, end=end, **kwargs)  # noqa: T003

    def on_init_dependencies(self) -> Iterable[ServiceT]:
        return self.services

    async def on_first_start(self) -> None:
        await self.default_on_first_start()

    async def default_on_first_start(self) -> None:
        if self.override_logging:
            self._setup_logging()
        await self.on_execute()
        if self.debug:
            await self._add_monitor()
        self.install_signal_handlers()

    async def on_execute(self) -> None:
        ...

    def _setup_logging(self) -> None:
        _loglevel: int = 0
        try:
            _loglevel = logging.setup_logging(
                log_level=self.log_level,
                log_file=self.log_file,
                log_handlers=self.log_handlers,
                logging_config=self.logging_config,
            )
        except Exception as exc:
            # TODO: Improve stack trace info.
            #       eg: If there is no existed parent directory for log_file,
            #       Only raises
            #       `CANNOT SETUP LOGGING: ValueError("Unable to configure handler 'default'")`
            #       That would be confused for users.
            try:
                self.stderr.write(f"CANNOT SETUP LOGGING: {exc!r} from\n")
                import traceback

                traceback.print_stack(file=self.stderr)
            except Exception:  # noqa: S110
                pass
            raise

        self.on_setup_root_logger(_logging.root, _loglevel)

        if self.redirect_stdouts:
            self._redirect_stdouts()

    def _redirect_stdouts(self) -> None:
        self.add_context(logging.redirect_stdouts(severity=self.redirect_stdouts_level))

    def on_setup_root_logger(self, logger: Logger, level: int) -> None:
        ...

    async def maybe_start_blockdetection(self) -> None:
        if self.debug:
            await self.blocking_detector.maybe_start()

    def install_signal_handlers(self) -> None:
        if sys.platform == "win32":
            self._install_signal_handlers_windows()
        else:
            self._install_signal_handlers_unix()

    def _install_signal_handlers_windows(self) -> None:
        signal.signal(signal.SIGTERM, self._on_win_sigterm)

    def _install_signal_handlers_unix(self) -> None:
        self.loop.add_signal_handler(signal.SIGINT, self._on_sigint)
        self.loop.add_signal_handler(signal.SIGTERM, self._on_sigterm)
        self.loop.add_signal_handler(signal.SIGUSR1, self._on_sigusr1)
        self.loop.add_signal_handler(signal.SIGUSR2, self._on_sigusr2)

    def _on_sigint(self) -> None:
        self.carp("-INT- -INT- -INT- -INT- -INT- -INT-")
        self._schedule_shutdown(signal.SIGINT)

    def _on_sigterm(self) -> None:
        self._schedule_shutdown(signal.SIGTERM)

    def _on_win_sigterm(self, signum: int, frame: Any) -> None:
        self._schedule_shutdown(signal.SIGTERM)

    def _on_sigusr1(self) -> None:
        self.add_future(self._cry())

    def _on_sigusr2(self) -> None:
        self._enter_debugger()

    async def _cry(self) -> None:
        logging.cry(file=self.stderr)

    def _enter_debugger(self) -> None:
        self.carp("Starting debugger...")
        import pdb  # noqa: T100

        pdb.set_trace()  # noqa: T100

    def _schedule_shutdown(self, signal: signal.Signals) -> None:
        if not self._signal_stop_time:
            self._signal_stop_time = self.loop.time()
            self._signal_stop_future = asyncio.ensure_future(
                self._stop_on_signal(signal), loop=self.loop
            )

    async def _stop_on_signal(self, signal: signal.Signals) -> None:
        self.log.info("Signal received: %s (%s)", signal, signal.value)
        await self.stop()
        maybe_cancel(self._starting_fut)

    def execute_from_commandline(self) -> NoReturn:
        self.start_system()
        with exiting(file=self.stderr):
            try:
                self.loop.run_until_complete(self.join())
            except asyncio.CancelledError:
                pass
            finally:
                self._shutdown_loop()
        # for mypy NoReturn
        raise SystemExit(EX_OK)

    def start_system(self) -> None:
        self._starting_fut = asyncio.ensure_future(self.start(), loop=self.loop)

    async def join(self) -> None:
        # TODO: Due to `object AsyncMock can't be used in 'await' expression`,
        #       have not be fully covered by unittests yet.
        if self._starting_fut is None:
            raise RuntimeError("Please start system before join it.")

        try:
            await self._starting_fut
        except MemoryError:
            raise
        except Exception as exc:
            self.log.exception("Error: %r", exc)
            raise
        finally:
            maybe_cancel(self._starting_fut)
            await self.on_worker_shutdown()
            await self.stop_and_shutdown()

    async def on_worker_shutdown(self) -> None:
        ...

    async def stop_and_shutdown(self) -> None:
        if self._signal_stop_future and not self._signal_stop_future.done():
            await self._signal_stop_future
        elif not self._stopped.is_set():
            await self.stop()

        await self._gather_all_after_stop()

    async def _gather_all_after_stop(self) -> None:
        # Gather futures created by us.
        self.log.info("Gathering service tasks...")
        with suppress(asyncio.CancelledError):
            await self._gather_futures()
        # Gather absolutely all asyncio futures.
        self.log.info("Gathering all futures...")
        await self._gather_all()

    def _shutdown_loop(self) -> None:
        try:
            # Wait until loop is fully stopped.
            while self.loop.is_running():
                self.log.info("Waiting for event loop to shutdown...")
                self.loop.stop()
                self.loop.run_until_complete(asyncio.sleep(1.0))
        except BaseException as exc:
            self.log.exception("Got exception while waiting: %r", exc)
        finally:
            # Then close the loop.
            fut = asyncio.ensure_future(self._sentinel_task(), loop=self.loop)
            self.loop.run_until_complete(fut)
            self.loop.stop()
            self.log.info("Closing event loop")
            self.loop.close()
            if self.crash_reason:
                self.log.critical(
                    "We experienced a crash! Reraising original exception..."
                )
                raise self.crash_reason from self.crash_reason

    async def _sentinel_task(self) -> None:
        await asyncio.sleep(1.0)

    async def _gather_all(self) -> None:
        # sleeps for at most 10 * 0.1s
        for _ in range(10):
            if not len(all_tasks(loop=self.loop)):
                break
            await asyncio.sleep(0.1)
        for task in all_tasks(loop=self.loop):
            task.cancel()

    async def on_started(self) -> None:
        if self.daemon:
            await self.wait_until_stopped()

    async def _add_monitor(self) -> Any:
        try:
            import aiomonitor
        except ImportError:
            self.log.warning("Cannot start console: aiomonitor is not installed")
        else:
            monitor = aiomonitor.start_monitor(
                loop=self.loop,
                port=self.console_port,
            )
            self.add_context(monitor)

    def _repr_info(self) -> str:
        return _repr(self.services)

    @property
    def blocking_detector(self) -> BlockingDetector:
        if self._blocking_detector is None:
            BlockDetector: Callable = symbol_by_name(self.BLOCK_DETECTOR)
            self._blocking_detector = BlockDetector(
                self.blocking_timeout,
                beacon=self.beacon,
                loop=self.loop,
            )
        return self._blocking_detector
