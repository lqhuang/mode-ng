.. _changelog:

================
 Change history
================

.. version-0.3.0

0.3.0
=====

:release-date: 2022-06-21
:release-by: Lanqing Huang (:github_user:`lqhuang`)

Now you can output log to file and console simultaneously.

- ``a742e99`` Remove redundant config files
- ``e3a464b`` Improve type hints
- ``73b0a8b`` Cleanup asyncio future utilities
- ``34c3d4a`` Improve code style and add an assertion
- ``634c93e`` Fix `logfile` only accepts `str` type and deprecate `sys.version` < (3, 8)
- ``1cbca46`` Tune config for mypy and flake8
- ``e7dd6b5`` Unify `setup.cfg` and `setup.py`

.. version-0.2.0

0.2.0
=====

:release-date: 2021-11-21
:release-by: Lanqing Huang (:github_user:`lqhuang`)

- ``f497657`` Tune bumpversion config
- ``bfa1e59`` Add more readme content
- ``1fa32cb`` Deprecate custom `cached_property`
- ``a9ce977`` 1. Fix timer wait twice before execution; 2. Add optional arg to exectue immediately
- ``e35d4cd`` Deprecate `mode.utils.compat` and `mode.utils.contexts`
- ``96b6293`` Deprecate `mode.utils.typing`

.. version-0.1.0

0.1.0
=====

:release-date: 2021-11-16
:release-by: Lanqing Huang (:github_user:`lqhuang`)

- Support python-3.10

- Friendly fork of ``faust-streaming/mode``: Initial release

- Nothing changes yet

.. version-previous-release:

previous-release
================

:release-date: 2021-10-14
:release-by: Taybin Rutkin (:github_user:`taybin`), Thomas Sarboni (:github_user:`max-k`)

- Support python-3.10
- format with black and isort
- add crontab timer from Faust (:github_user:`lqhuang`)
- Friendly fork of ask/mode : Initial release
- Move to new travis-ci.com domain
- Add tests on Python 3.8.1-3.8.6
- Fix broken tests
- Add Python 3.9 support
