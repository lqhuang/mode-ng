"""Type classes for :mod:`mode.signals`."""
from __future__ import annotations

from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    MutableMapping,
    MutableSet,
    Optional,
    Type,
    TypeVar,
    Union,
    no_type_check,
)

import abc
from asyncio.events import AbstractEventLoop
from weakref import ReferenceType

from mypy_extensions import KwArg, NamedArg, VarArg

__all__ = [
    "BaseSignalT",
    "FilterReceiverMapping",
    "SignalHandlerT",
    "SignalHandlerRefT",
    "SignalT",
    "SyncSignalT",
    "T",
    "T_contra",
]

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)

SignalHandlerT = Union[
    Callable[
        [T, VarArg(), NamedArg("BaseSignalT", name="signal"), KwArg()],
        None,
    ],
    Callable[
        [T, VarArg(), NamedArg("BaseSignalT", name="signal"), KwArg()],
        Awaitable[None],
    ],
]

SignalHandlerRefT = Union[Callable[[], SignalHandlerT], ReferenceType[SignalHandlerT]]

FilterReceiverMapping = MutableMapping[Any, MutableSet[SignalHandlerRefT]]


class BaseSignalT(Generic[T]):
    """Base type for all signals."""

    name: str
    owner: Optional[Type]

    @abc.abstractmethod
    def __init__(
        self,
        *,
        name: str = None,
        owner: Type = None,
        loop: AbstractEventLoop = None,
        default_sender: Any = None,
        receivers: MutableSet[SignalHandlerRefT] = None,
        filter_receivers: FilterReceiverMapping = None,
    ) -> None:
        ...

    @abc.abstractmethod
    def clone(self, **kwargs: Any) -> BaseSignalT:
        ...

    @abc.abstractmethod
    def with_default_sender(self, sender: Any = None) -> BaseSignalT:
        ...

    @abc.abstractmethod
    def connect(self, fun: SignalHandlerT, **kwargs: Any) -> Callable:
        ...

    @abc.abstractmethod
    def disconnect(
        self, fun: SignalHandlerT, *, sender: Any = None, weak: bool = True
    ) -> None:
        ...


class SignalT(BaseSignalT[T]):
    """Base class for all async signals (using ``async def``)."""

    @abc.abstractmethod
    async def __call__(self, sender: T_contra, *args: Any, **kwargs: Any) -> None:
        ...

    @abc.abstractmethod
    async def send(self, sender: T_contra, *args: Any, **kwargs: Any) -> None:
        ...

    @no_type_check
    @abc.abstractmethod
    def clone(self, **kwargs: Any) -> SignalT:
        ...

    @no_type_check
    @abc.abstractmethod
    def with_default_sender(self, sender: Any = None) -> SignalT:
        ...


class SyncSignalT(BaseSignalT[T]):
    """Base class for all synchronous signals (using regular ``def``)."""

    @abc.abstractmethod
    def __call__(self, sender: T_contra, *args: Any, **kwargs: Any) -> None:
        ...

    @abc.abstractmethod
    def send(self, sender: T_contra, *args: Any, **kwargs: Any) -> None:
        ...

    @no_type_check
    @abc.abstractmethod
    def clone(self, **kwargs: Any) -> SyncSignalT:
        ...

    @no_type_check
    @abc.abstractmethod
    def with_default_sender(self, sender: Any = None) -> SyncSignalT:
        ...
