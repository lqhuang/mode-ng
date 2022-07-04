from typing import Optional, Type

from types import TracebackType

ExcInfo = tuple[Type[BaseException], BaseException, Optional[TracebackType]]
