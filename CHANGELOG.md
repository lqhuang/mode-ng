# Changelong

## 0.3.1 - 2022-06-27

release-by: Lanqing Huang (@lqhuang)

No features and bugs updates, only project scaffold is improved.

- tests: Fix logging tests and simplified test requirements
- chore: Use `pyproject.toml` to declare metadata
- chore: Switch to `src` layout

## 0.3.0 - 2022-06-21

release-by: Lanqing Huang (@lqhuang)

Now you can output log to file and console simultaneously.

- Remove redundant config files
- Improve type hints
- Cleanup asyncio future utilities
- Improve code style and add an assertion
- Fix `logfile` only accepts `str` type and deprecate `sys.version` < (3, 8)
- Tune config for mypy and flake8
- Unify `setup.cfg` and `setup.py`

## 0.2.0 - 2021-11-21

release-by: Lanqing Huang (@lqhuang)

- Tune bumpversion config
- Add more readme content
- Deprecate custom `cached_property`
- (1) Fix timer wait twice before execution; (2) Add optional arg to exectue immediately
- Deprecate `mode.utils.compat` and `mode.utils.contexts`
- Deprecate `mode.utils.typing`

## 0.1.0 - 2021-11-16

release-by: Lanqing Huang (@lqhuang)

- Support python-3.10
- Friendly fork of `faust-streaming/mode`: Initial release
- Nothing changes yet

## Previous release - 2021-10-14

release-by: Taybin Rutkin (@taybin), Thomas Sarboni (@max-k)

- Support python-3.10
- Format with black and isort
- Add crontab timer from Faust (@lqhuang)
- Friendly fork of `ask/mode`: Initial release
- Move to new travis-ci.com domain
- Add tests on Python 3.8.1-3.8.6
- Fix broken tests
- Add Python 3.9 support
