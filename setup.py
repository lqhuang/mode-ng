#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from platform import python_implementation

from setuptools import find_packages, setup

NAME = "mode-ng"
EXTENSIONS = {"eventlet", "gevent", "uvloop"}
E_UNSUPPORTED_PYTHON = "%s 0.2.0 requires %%s %%s or later!" % (NAME,)
PYIMP = python_implementation()

if sys.version_info < (3, 10):
    raise Exception(E_UNSUPPORTED_PYTHON % (PYIMP, "3.10"))

# -*- Installation Requires -*-
def strip_comments(line):
    return line.split("#", 1)[0].strip()


def _pip_requirement(req):
    if req.startswith("-r "):
        _, path = req.split()
        return reqs(*path.split("/"))
    return [req]


def _reqs(*f):
    path = (Path.cwd() / "requirements").joinpath(*f)
    reqs = (strip_comments(line) for line in path.open().readlines())
    return [_pip_requirement(r) for r in reqs if r]


def reqs(*f):
    return [req for subreq in _reqs(*f) for req in subreq]


def extras(*p):
    """Parse requirement in the requirements/extras/ directory."""
    return reqs("extras", *p)


def extras_require():
    """Get map of all extra requirements."""
    return {x: extras(x + ".txt") for x in EXTENSIONS}


# -*- %%% -*-

packages = find_packages(
    exclude=["tests", "tests.*", "docs", "docs.*", "examples", "examples.*"],
)
assert not any(package.startswith("tests.") for package in packages)


setup(
    name=NAME,
    platforms=["any"],
    packages=packages,
    include_package_data=True,
    # PEP-561: https://www.python.org/dev/peps/pep-0561/
    package_data={"mode": ["py.typed"]},
    zip_safe=False,
    install_requires=reqs("default.txt"),
    tests_require=reqs("test.txt"),
    extras_require=extras_require(),
    python_requires=">=3.10",
)
