"""Object utilities."""
from __future__ import annotations

import typing
from typing import (
    AbstractSet,
    Any,
    ClassVar,
    ForwardRef,
    Generic,
    Iterable,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    TypeVar,
    cast,
)

import abc
import collections.abc
import sys
from contextlib import suppress
from decimal import Decimal
from functools import total_ordering
from pathlib import Path

try:
    from typing import _eval_type  # type: ignore
except ImportError:

    def _eval_type(t, globalns, localns, recursive_guard=frozenset()):  # type: ignore
        return t


try:
    from typing import _type_check  # type: ignore
except ImportError:

    def _type_check(arg, msg, is_argument=True, module=None):  # type: ignore
        return arg


try:
    from typing import _ClassVar  # type: ignore
except ImportError:  # pragma: no cover
    # CPython 3.7
    from typing import _GenericAlias  # type: ignore

    def _is_class_var(x: Any) -> bool:  # noqa
        return isinstance(x, _GenericAlias) and x.__origin__ is ClassVar

else:  # pragma: no cover
    # CPython 3.6
    def _is_class_var(x: Any) -> bool:
        return type(x) is _ClassVar


__all__ = [
    "FieldMapping",
    "DefaultsMapping",
    "Unordered",
    "KeywordReduce",
    "InvalidAnnotation",
    "abc_compatible_with_init_subclass",
    "qualname",
    "shortname",
    "canoname",
    "canonshortname",
    "annotations",
    "eval_type",
    "iter_mro_reversed",
    "guess_polymorphic_type",
    "label",
    "shortlabel",
]

# Workaround for https://bugs.python.org/issue29581
try:

    @typing.no_type_check
    class _InitSubclassCheck(metaclass=abc.ABCMeta):
        ident: int

        def __init_subclass__(cls, *args: Any, ident: int = 808, **kwargs: Any) -> None:
            cls.ident = ident
            super().__init__(*args, **kwargs)

    @typing.no_type_check
    class _UsingKwargsInNew(_InitSubclassCheck, ident=909):
        ...

except TypeError:
    abc_compatible_with_init_subclass = False
else:
    abc_compatible_with_init_subclass = True

_T = TypeVar("_T")
RT = TypeVar("RT")

#: Mapping of attribute name to attribute type.
FieldMapping = Mapping[str, type]

#: Mapping of attribute name to attributes default value.
DefaultsMapping = Mapping[str, Any]

SET_TYPES: tuple[type, ...] = (
    AbstractSet,
    frozenset,
    MutableSet,
    set,
    collections.abc.Set,
)
LIST_TYPES: tuple[type, ...] = (
    list,
    Sequence,
    MutableSequence,
    collections.abc.Sequence,
)
DICT_TYPES: tuple[type, ...] = (
    dict,
    Mapping,
    MutableMapping,
    collections.abc.Mapping,
)
# XXX cast required for mypy bug
# "expression has type tuple[_SpecialForm]"
TUPLE_TYPES: tuple[type, ...] = cast(tuple[type, ...], (tuple,))


class InvalidAnnotation(Exception):
    """Raised by :func:`annotations` when encountering an invalid type."""


@total_ordering
class Unordered(Generic[_T]):
    """Shield object from being ordered in heapq/``__le__``/etc."""

    # Used to put anything inside a heapq, even things that cannot be ordered
    # like dicts and lists.

    def __init__(self, value: _T) -> None:
        self.value = value

    def __le__(self, other: Any) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {self.value!r}>"


def _restore_from_keywords(typ: type, kwargs: dict) -> Any:
    # This function is used to restore pickled KeywordReduce object.
    return typ(**kwargs)


class KeywordReduce:
    """Mixin class for objects that can be "pickled".

    "Pickled" means the object can be serialiazed using the Python binary
    serializer -- the :mod:`pickle` module.

    Python objects are made pickleable through defining the ``__reduce__``
    method, that returns a tuple of:
    ``(restore_function, function_starargs)``::

        class X:

            def __init__(self, arg1, kw1=None):
                self.arg1 = arg1
                self.kw1 = kw1

            def __reduce__(self) -> Tuple[Callable, Tuple[Any, ...]]:
                return type(self), (self.arg1, self.kw1)

    This is *tedious* since this means you cannot accept ``**kwargs`` in the
    constructur, so what we do is define a ``__reduce_keywords__``
    argument that returns a dict instead::

        class X:

            def __init__(self, arg1, kw1=None):
                self.arg1 = arg1
                self.kw1 = kw1

            def __reduce_keywords__(self) -> Mapping[str, Any]:
                return {
                    'arg1': self.arg1,
                    'kw1': self.kw1,
                }
    """

    def __reduce_keywords__(self) -> Mapping:
        raise NotImplementedError()

    def __reduce__(self) -> tuple:
        return _restore_from_keywords, (type(self), self.__reduce_keywords__())


def qualname(obj: Any) -> str:
    """Get object qualified name."""
    if not hasattr(obj, "__name__") and hasattr(obj, "__class__"):
        obj = obj.__class__
    name = getattr(obj, "__qualname__", obj.__name__)
    return ".".join((obj.__module__, name))


def shortname(obj: Any) -> str:
    """Get object name (non-qualified)."""
    if not hasattr(obj, "__name__") and hasattr(obj, "__class__"):
        obj = obj.__class__
    return ".".join((obj.__module__, obj.__name__))


def canoname(obj: Any, *, main_name: str = None) -> str:
    """Get qualname of obj, trying to resolve the real name of ``__main__``."""
    name = qualname(obj)
    parts = name.split(".")
    if parts[0] == "__main__":
        return ".".join([main_name or _detect_main_name()] + parts[1:])
    return name


def canonshortname(obj: Any, *, main_name: str = None) -> str:
    """Get non-qualified name of obj, resolve real name of ``__main__``."""
    name = shortname(obj)
    parts = name.split(".")
    if parts[0] == "__main__":
        return ".".join([main_name or _detect_main_name()] + parts[1:])
    return name


def _detect_main_name() -> str:  # pragma: no cover
    try:
        filename = sys.modules["__main__"].__file__
    except (AttributeError, KeyError):  # ipython/REPL
        return "__main__"
    else:
        path = Path(filename).absolute()
        node = path.parent
        seen = []
        while node:
            if (node / "__init__.py").exists():
                seen.append(node.stem)
                node = node.parent
            else:
                break
        return ".".join(seen + [path.stem])


def reveal_annotations(
    cls: type,
    *,
    stop: type = object,
    invalid_types: set = None,
    alias_types: Mapping = None,
    skip_classvar: bool = False,
    globalns: dict[str, Any] = None,
    localns: dict[str, Any] = None,
) -> tuple[FieldMapping, DefaultsMapping]:
    """Get class field definition in MRO order.

    Arguments:
        cls: Class to get field information from.
        stop: Base class to stop at (default is ``object``).
        invalid_types: Set of types that if encountered should raise
          :exc:`InvalidAnnotation` (does not test for subclasses).
        alias_types: Mapping of original type to replacement type.
        skip_classvar: Skip attributes annotated with
            :class:`typing.ClassVar`.
        globalns: Global namespace to use when evaluating forward
            references (see :class:`typing.ForwardRef`).
        localns: Local namespace to use when evaluating forward
            references (see :class:`typing.ForwardRef`).

    Returns:
        tuple[FieldMapping, DefaultsMapping]: tuple with two dictionaries,
            the first containing a map of field names to their types,
            the second containing a map of field names to their default
            value.  If a field is not in the second map, it means the field
            is required.

    Raises:
        InvalidAnnotation: if a list of invalid types are provided and an
            invalid type is encountered.

    Examples:
        .. code-block:: text

            >>> class Point:
            ...    x: float
            ...    y: float

            >>> class 3DPoint(Point):
            ...     z: float = 0.0

            >>> fields, defaults = annotations(3DPoint)
            >>> fields
            {'x': float, 'y': float, 'z': 'float'}
            >>> defaults
            {'z': 0.0}
    """
    fields: dict[str, type] = {}
    defaults: dict[str, Any] = {}
    for subcls in iter_mro_reversed(cls, stop=stop):
        defaults.update(subcls.__dict__)
        with suppress(AttributeError):
            fields.update(
                local_annotations(
                    subcls,
                    invalid_types=invalid_types,
                    alias_types=alias_types,
                    skip_classvar=skip_classvar,
                    globalns=globalns,
                    localns=localns,
                )
            )
    return fields, defaults


def local_annotations(
    cls: type,
    *,
    invalid_types: set = None,
    alias_types: Mapping = None,
    skip_classvar: bool = False,
    globalns: dict[str, Any] = None,
    localns: dict[str, Any] = None,
) -> Iterable[tuple[str, type]]:
    return _resolve_refs(
        cls.__annotations__,
        globalns if globalns is not None else _get_globalns(cls),
        localns,
        invalid_types or set(),
        alias_types or {},
        skip_classvar,
    )


def _resolve_refs(
    d: dict[str, Any],
    globalns: dict[str, Any] = None,
    localns: dict[str, Any] = None,
    invalid_types: set = None,
    alias_types: Mapping = None,
    skip_classvar: bool = False,
) -> Iterable[tuple[str, type]]:
    invalid_types = invalid_types or set()
    alias_types = alias_types or {}
    for k, v in d.items():
        v = eval_type(v, globalns, localns, invalid_types, alias_types)
        if skip_classvar and _is_class_var(v):
            pass
        else:
            yield k, v


def eval_type(
    typ: Any,
    globalns: dict[str, Any] = None,
    localns: dict[str, Any] = None,
    invalid_types: set = None,
    alias_types: Mapping = None,
) -> type:
    """Convert (possible) string annotation to actual type.

    Examples:
        >>> eval_type('List[int]') == typing.List[int]
    """
    invalid_types = invalid_types or set()
    alias_types = alias_types or {}
    if isinstance(typ, str):
        typ = ForwardRef(typ)
    if isinstance(typ, ForwardRef):
        # On 3.6/3.7 _eval_type crashes if str references ClassVar
        typ = _ForwardRef_safe_eval(typ, globalns, localns)
    typ = _eval_type(typ, globalns, localns)
    if typ in invalid_types:
        raise InvalidAnnotation(typ)
    return alias_types.get(typ, typ)


def _ForwardRef_safe_eval(
    ref: ForwardRef,
    globalns: dict[str, Any] = None,
    localns: dict[str, Any] = None,
) -> type:
    # On 3.6/3.7 ForwardRef._evaluate crashes if str references ClassVar
    if not ref.__forward_evaluated__:
        if globalns is None and localns is None:
            globalns = localns = {}
        elif globalns is None:
            globalns = localns
        elif localns is None:
            localns = globalns
        val = eval(ref.__forward_code__, globalns, localns)  # noqa: S307
        if not _is_class_var(val):
            val = _type_check(val, "Forward references must evaluate to types.")
        ref.__forward_value__ = val
        ref.__forward_evaluated__ = True
    return ref.__forward_value__


def _get_globalns(typ: type) -> dict[str, Any]:
    return sys.modules[typ.__module__].__dict__


def iter_mro_reversed(cls: type, stop: type) -> Iterable[type]:
    """Iterate over superclasses, in reverse Method Resolution Order.

    The stop argument specifies a base class that when seen will
    stop iterating (well actually start, since this is in reverse, see Example
    for demonstration).

    Arguments:
        cls (Type): Target class.
        stop (Type): A base class in which we stop iteration.

    Notes:
        The last item produced will be the class itself (`cls`).

    Examples:
        >>> class A: ...
        >>> class B(A): ...
        >>> class C(B): ...

        >>> list(iter_mro_reverse(C, object))
        [A, B, C]

        >>> list(iter_mro_reverse(C, A))
        [B, C]

    Yields:
        Iterable[Type]: every class.
    """
    wanted = False
    for subcls in reversed(cls.__mro__):
        if wanted:
            yield cast(type, subcls)
        else:
            wanted = subcls == stop


def remove_optional(typ: type) -> type:
    _, typ = _remove_optional(typ)
    return typ


def is_union(typ: type) -> bool:
    name = typ.__class__.__name__
    return any(
        [
            name == "_UnionGenericAlias",  # 3.9
            name == "_GenericAlias" and typ.__origin__ is typing.Union,  # 3.7
            name == "_Union",  # 3.6
        ],
    )


def is_optional(typ: type) -> bool:
    if is_union(typ):
        args = getattr(typ, "__args__", ())
        return any([True for arg in args if arg is None or arg is type(None)])  # noqa
    return False


def _remove_optional(typ: type, *, find_origin: bool = False) -> tuple[List[Any], type]:
    args = getattr(typ, "__args__", ())
    if is_union(typ):
        # 3.7+: Optional[List[int]] -> Union[List[int], NoneType]
        # 3.6:  Optional[List[int]] -> Union[List[int], type(None)]
        # returns: ((int,), list)
        found_None = False
        union_type_args: list | None = None
        union_type: type | None = None
        for arg in args:
            if arg is None or arg is type(None):  # noqa
                found_None = True
            else:
                union_type_args = getattr(arg, "__args__", ())
                union_type = arg
                if find_origin:
                    if union_type is not None and sys.version_info.minor == 6:
                        union_type = _py36_maybe_unwrap_GenericMeta(union_type)
                    else:
                        union_type = getattr(arg, "__origin__", arg)
        if union_type is not None and found_None:
            return cast(list, union_type_args), union_type
    if find_origin:
        if hasattr(typ, "__origin__"):
            # List[int] -> ((int,), list)
            typ = _py36_maybe_unwrap_GenericMeta(typ)

    return args, typ


def _py36_maybe_unwrap_GenericMeta(typ: type) -> type:
    if typ.__class__.__name__ == "GenericMeta":  # Py3.6
        orig_bases = typ.__orig_bases__
        if orig_bases and orig_bases[0] in (list, tuple, dict, set):
            return cast(type, orig_bases[0])
    return cast(type, getattr(typ, "__origin__", typ))


def guess_polymorphic_type(
    typ: type,
    *,
    set_types: tuple[type, ...] = SET_TYPES,
    list_types: tuple[type, ...] = LIST_TYPES,
    tuple_types: tuple[type, ...] = TUPLE_TYPES,
    dict_types: tuple[type, ...] = DICT_TYPES,
) -> tuple[type, type]:
    """Try to find the polymorphic and concrete type of an abstract type.

    Returns tuple of ``(polymorphic_type, concrete_type)``.

    Examples:
        >>> guess_polymorphic_type(list[int])
        (list, int)

        >>> guess_polymorphic_type(Optional[list[int]])
        (list, int)

        >>> guess_polymorphic_type(MutableMapping[int, str])
        (dict, str)
    """
    args, typ = _remove_optional(typ, find_origin=True)
    if typ is not str and typ is not bytes:
        if issubclass(typ, tuple_types):
            # tuple[x]
            return tuple, _unary_type_arg(args)
        elif issubclass(typ, set_types):
            # set[x]
            return set, _unary_type_arg(args)
        elif issubclass(typ, list_types):
            # list[x]
            return list, _unary_type_arg(args)
        elif issubclass(typ, dict_types):
            # dict[_, x]
            return dict, args[1] if args and len(args) > 1 else Any
    raise TypeError(f"Not a generic type: {typ!r}")


guess_concrete_type = guess_polymorphic_type  # XXX compat


def _unary_type_arg(args: list[type]) -> Any:
    return args[0] if args else Any


def label(s: Any) -> str:
    """Return the name of an object as string."""
    return _label("label", s)


def shortlabel(s: Any) -> str:
    """Return the shortened name of an object as string."""
    return _label("shortlabel", s)


def _label(
    label_attr: str,
    s: Any,
    pass_types: tuple[type, ...] = (str,),
    str_types: tuple[type, ...] = (str, int, float, Decimal),
) -> str:
    if isinstance(s, pass_types):
        return cast(str, s)
    elif isinstance(s, str_types):
        return str(s)
    return str(
        getattr(s, label_attr, None)
        or getattr(s, "name", None)
        or getattr(s, "__qualname__", None)
        or getattr(s, "__name__", None)
        or getattr(type(s), "__qualname__", None)
        or type(s).__name__
    )
