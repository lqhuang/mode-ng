#!/usr/bin/env python
from pathlib import Path

from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
from setuptools import setup

EXTENSIONS = {"eventlet", "gevent", "uvloop"}

pattern = "requirements/**/*.txt"
requirements_files = Path(__file__).parent.glob(pattern)

session = PipSession()
requirements = {
    each.stem: list(
        i.requirement for i in parse_requirements(str(each), session=session)
    )
    for each in requirements_files
}

if "all" not in requirements:
    requirements["all"] = set().union(  # type: ignore[assignment]
        *(
            v
            for k, v in requirements.items()
            if k not in ("dev", "test", "release")
        )
    )

install_requires = requirements.pop("default", [])
extras_require = {ext: requirements[ext] for ext in EXTENSIONS}

if __name__ == "__main__":
    setup(
        # PEP-561: https://www.python.org/dev/peps/pep-0561/
        include_package_data=True,
        package_data={"mode": ["py.typed"]},
        install_requires=install_requires,
        extras_require=extras_require,
    )
