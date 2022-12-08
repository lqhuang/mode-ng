"""Type classes for :mod:`mode.supervisors`."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

import abc

from mode.utils.times import Seconds

from .services import ServiceT

__all__ = ["SupervisorStrategyT"]

ReplacementT = Callable[[ServiceT, int], Awaitable[ServiceT]]


class SupervisorStrategyT(ServiceT):
    """Base type for all supervisor strategies."""

    max_restarts: float
    over: float
    raises: type[BaseException]

    @abc.abstractmethod
    def __init__(
        self,
        *services: ServiceT,
        max_restarts: Seconds = 100.0,
        over: Seconds = 1.0,
        raises: type[BaseException] = None,
        replacement: ReplacementT = None,
        **kwargs: Any,
    ) -> None:
        self.replacement: ReplacementT | None = replacement

    @abc.abstractmethod
    def wakeup(self) -> None:
        ...

    @abc.abstractmethod
    def add(self, *services: ServiceT) -> None:
        ...

    @abc.abstractmethod
    def discard(self, *services: ServiceT) -> None:
        ...

    @abc.abstractmethod
    def service_operational(self, service: ServiceT) -> bool:
        ...

    @abc.abstractmethod
    async def restart_service(self, service: ServiceT) -> None:
        ...
