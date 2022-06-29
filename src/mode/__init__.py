"""AsyncIO Service-based programming."""
# :copyright: (c) 2017-2020, Robinhood Markets
#             (c) 2020-2021, faust-streaming Org
#             (c) 2021-2022, Lanqing Huang
#             All rights reserved.
# :license:   BSD (3 Clause), see LICENSE for more details.
from typing import TYPE_CHECKING, Any, Mapping, Sequence

import sys
from importlib.metadata import version
from types import ModuleType  # noqa

if TYPE_CHECKING:  # pragma: no cover
    from .services import Service, task, timer  # noqa: E402
    from .signals import BaseSignal, Signal, SyncSignal  # noqa: E402
    from .supervisors import CrashingSupervisor  # noqa: E402
    from .supervisors import (
        ForfeitOneForAllSupervisor,
        ForfeitOneForOneSupervisor,
        OneForAllSupervisor,
        OneForOneSupervisor,
        SupervisorStrategy,
    )
    from .types.services import ServiceT  # noqa: E402
    from .types.signals import BaseSignalT, SignalT, SyncSignalT  # noqa: E402
    from .types.supervisors import SupervisorStrategyT  # noqa: E402
    from .utils.logging import (  # noqa: E402
        flight_recorder,
        get_logger,
        setup_logging,
    )
    from .utils.objects import label, shortlabel  # noqa: E402
    from .utils.times import Seconds, want_seconds  # noqa: E402
    from .worker import Worker  # noqa: E402

__package_name__ = "mode-ng"
__version__ = version(__package_name__)

__all__ = [
    "BaseSignal",
    "BaseSignalT",
    "Service",
    "Signal",
    "SignalT",
    "SyncSignal",
    "SyncSignalT",
    "ForfeitOneForAllSupervisor",
    "ForfeitOneForOneSupervisor",
    "OneForAllSupervisor",
    "OneForOneSupervisor",
    "SupervisorStrategy",
    "CrashingSupervisor",
    "ServiceT",
    "SupervisorStrategyT",
    "Seconds",
    "want_seconds",
    "get_logger",
    "setup_logging",
    "label",
    "shortlabel",
    "Worker",
    "task",
    "timer",
    "flight_recorder",
]

# Lazy loading.
# - See werkzeug/__init__.py for the rationale behind this.
# - `werkzeug` has deprecated lazy importer.
# - Here is pinned: https://github.com/pallets/werkzeug/blob/c3322bd51fb511fa4be6f208ad048f87d57694d7/src/werkzeug/__init__.py

# This import magic raises concerns quite often which is why the implementation
# and motivation is explained here in detail now.
#
# The majority of the functions and classes provided by Werkzeug work on the
# HTTP and WSGI layer.  There is no useful grouping for those which is why
# they are all importable from "werkzeug" instead of the modules where they are
# implemented.  The downside of that is, that now everything would be loaded at
# once, even if unused.
#
# The implementation of a lazy-loading module in this file replaces the
# werkzeug package when imported from within.  Attribute access to the werkzeug
# module will then lazily import from the modules that implement the objects.


# import mapping to objects in other modules
all_by_module: Mapping[str, Sequence[str]] = {
    "mode.services": ["Service", "task", "timer"],
    "mode.signals": ["BaseSignal", "Signal", "SyncSignal"],
    "mode.supervisors": [
        "ForfeitOneForAllSupervisor",
        "ForfeitOneForOneSupervisor",
        "OneForAllSupervisor",
        "OneForOneSupervisor",
        "SupervisorStrategy",
        "CrashingSupervisor",
    ],
    "mode.types.services": ["ServiceT"],
    "mode.types.signals": ["BaseSignalT", "SignalT", "SyncSignalT"],
    "mode.types.supervisors": ["SupervisorStrategyT"],
    "mode.utils.times": ["Seconds", "want_seconds"],
    "mode.utils.logging": ["flight_recorder", "get_logger", "setup_logging"],
    "mode.utils.objects": ["label", "shortlabel"],
    "mode.worker": ["Worker"],
}

object_origins = {}
for module, items in all_by_module.items():
    for item in items:
        object_origins[item] = module


class _module(ModuleType):
    """Automatically import objects from the modules."""

    def __getattr__(self, name: str) -> Any:
        if name in object_origins:
            module = __import__(object_origins[name], None, None, [name])
            for extra_name in all_by_module[module.__name__]:
                setattr(self, extra_name, getattr(module, extra_name))
            return getattr(module, name)
        return ModuleType.__getattribute__(self, name)

    def __dir__(self) -> Sequence[str]:
        result = list(new_module.__all__)
        result.extend(
            (
                "__file__",
                "__doc__",
                "__all__",
                "__name__",
                "__package__",
                "__version__",
            )
        )
        return result


# keep a reference to this module so that it's not garbage collected
old_module = sys.modules[__name__]

# setup the new module and patch it into the dict of loaded modules
new_module = sys.modules[__name__] = _module(__name__)
new_module.__dict__.update(
    {
        "__file__": __file__,
        "__doc__": __doc__,
        "__all__": tuple(object_origins),
        "__name__": __name__,
        "__version__": __version__,
        "__package__": __package__,
    }
)
