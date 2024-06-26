"""Type classes for :mod:`mode.services`."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Awaitable,
    ContextManager,
    Coroutine,
    MutableMapping,
    TypeVar,
)

import abc
import asyncio
from contextlib import AsyncExitStack, ExitStack

from mode.utils.types.trees import NodeT

if TYPE_CHECKING:
    from .supervisors import SupervisorStrategyT

__all__ = [
    "DiagT",
    "ServiceT",
]

T = TypeVar("T")

AsyncFun = Awaitable[T] | Coroutine[Any, Any, T]


class DiagT(abc.ABC):
    """Diag keeps track of a services diagnostic flags."""

    flags: set[str]
    last_transition: MutableMapping[str, float]

    @abc.abstractmethod
    def __init__(self, service: ServiceT) -> None: ...

    @abc.abstractmethod
    def set_flag(self, flag: str) -> None: ...

    @abc.abstractmethod
    def unset_flag(self, flag: str) -> None: ...


class ServiceT(AsyncContextManager):
    """Abstract type for an asynchronous service that can be started/stopped.

    See Also:
        :class:`mode.Service`.
    """

    Diag: type[DiagT]
    diag: DiagT
    async_exit_stack: AsyncExitStack
    exit_stack: ExitStack

    shutdown_timeout: float
    wait_for_shutdown: bool = False
    restart_count: int = 0
    supervisor: SupervisorStrategyT | None = None
    _loop: asyncio.AbstractEventLoop | None

    @abc.abstractmethod
    def __init__(
        self,
        *,
        beacon: NodeT | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None: ...

    @abc.abstractmethod
    def add_dependency(self, service: ServiceT) -> ServiceT: ...

    @abc.abstractmethod
    async def add_runtime_dependency(self, service: ServiceT) -> ServiceT: ...

    @abc.abstractmethod
    async def add_async_context(self, context: AsyncContextManager) -> Any: ...

    @abc.abstractmethod
    def add_context(self, context: ContextManager) -> Any: ...

    @abc.abstractmethod
    async def start(self) -> None: ...

    @abc.abstractmethod
    async def maybe_start(self) -> bool: ...

    @abc.abstractmethod
    async def crash(self, reason: BaseException) -> None: ...

    @abc.abstractmethod
    def _crash(self, reason: BaseException) -> None: ...

    @abc.abstractmethod
    async def stop(self) -> None: ...

    @abc.abstractmethod
    def service_reset(self, restart: bool = True) -> None: ...

    @abc.abstractmethod
    async def restart(self) -> None: ...

    @abc.abstractmethod
    async def wait_until_stopped(self) -> None: ...

    @abc.abstractmethod
    def set_shutdown(self) -> None: ...

    @abc.abstractmethod
    def _repr_info(self) -> str: ...

    @property
    @abc.abstractmethod
    def started(self) -> bool: ...

    @property
    @abc.abstractmethod
    def crashed(self) -> bool: ...

    @property
    @abc.abstractmethod
    def should_stop(self) -> bool: ...

    @property
    @abc.abstractmethod
    def state(self) -> str: ...

    @property
    @abc.abstractmethod
    def label(self) -> str: ...

    @property
    @abc.abstractmethod
    def shortlabel(self) -> str: ...

    @property
    def beacon(self) -> NodeT: ...

    @beacon.setter
    def beacon(self, beacon: NodeT) -> None: ...

    @property
    @abc.abstractmethod
    def loop(self) -> asyncio.AbstractEventLoop: ...

    @loop.setter
    def loop(self, loop: asyncio.AbstractEventLoop) -> None: ...

    @property
    @abc.abstractmethod
    def crash_reason(self) -> BaseException | None: ...

    @crash_reason.setter
    def crash_reason(self, reason: BaseException | None) -> None: ...
