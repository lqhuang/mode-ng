"""AsyncIO Service-based programming."""
# :copyright: (c) 2017-2020, Robinhood Markets
#             (c) 2020-2021, faust-streaming Org
#             (c) 2021-2022, Lanqing Huang
#             All rights reserved.
# :license:   BSD (3 Clause), see LICENSE for more details.
from typing import Mapping, Sequence

from importlib.metadata import version

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
from .utils.logging import flight_recorder, get_logger, setup_logging  # noqa: E402
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

__all_by_module: Mapping[str, Sequence[str]] = {
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
