from types import TracebackType

ExcInfo = tuple[type[BaseException], BaseException, TracebackType | None]
