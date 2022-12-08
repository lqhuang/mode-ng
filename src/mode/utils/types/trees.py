"""Type classes for :mod:`mode.utils.trees`."""
from __future__ import annotations

from typing import Any, Generic, Iterator, TypeVar

import abc

from .graphs import DependencyGraphT

__all__ = ["NodeT"]

_T = TypeVar("_T")


class NodeT(Generic[_T]):
    """Node in a tree data structure."""

    children: list[Any]
    data: Any = None

    @classmethod
    @abc.abstractmethod
    def _new_node(cls, data: _T, **kwargs: Any) -> NodeT:
        ...

    @abc.abstractmethod
    def new(self, data: _T) -> NodeT:
        ...

    @abc.abstractmethod
    def add(self, data: _T | NodeT[_T]) -> None:
        ...

    @abc.abstractmethod
    def add_deduplicate(self, data: _T | NodeT[_T]) -> None:
        ...

    @abc.abstractmethod
    def discard(self, data: _T) -> None:
        ...

    @abc.abstractmethod
    def reattach(self, parent: NodeT) -> NodeT:
        ...

    @abc.abstractmethod
    def traverse(self) -> Iterator[NodeT]:
        ...

    @abc.abstractmethod
    def walk(self) -> Iterator[NodeT]:
        ...

    @abc.abstractmethod
    def as_graph(self) -> DependencyGraphT:
        ...

    @abc.abstractmethod
    def detach(self, parent: NodeT) -> NodeT:
        ...

    @property
    @abc.abstractmethod
    def parent(self) -> NodeT | None:
        ...

    @parent.setter
    def parent(self, node: NodeT) -> None:
        ...

    @property
    @abc.abstractmethod
    def root(self) -> NodeT | None:
        ...

    @root.setter
    def root(self, node: NodeT) -> None:
        ...

    @property
    @abc.abstractmethod
    def depth(self) -> int:
        ...

    @property
    @abc.abstractmethod
    def path(self) -> str:
        ...
