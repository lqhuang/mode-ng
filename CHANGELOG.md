# Changelong

## 0.5.0 - 2022-10-20

release-by: Lanqing Huang (@lqhuang)

From `mode-ng-0.5.0`, `Worker` is able to be embeded in other codes without terminating all while worker shutdown.

- [**breaking**] Seperate `start` and `join` into two functions
- [**breaking**] Enable `start_and_join` without shutdown loop
- Rebuild docs gen scripts
- Tune makefile

## 0.4.0 - 2022-07-04

release-by: Lanqing Huang (@lqhuang)

This version is still major in refactoring and tuning. There are serveral breaking changes. Some notable changes including:

1. `on_init` method of `Service` is removed from this version.
2. `want_seconds` function do not accept `None` as input.
3. This may most influenced changes: args `loglevel`, `logfile`, `loghandlers` of `Worker`
   has been renamed to `log_level`, `log_file` and `log_handlers` in order to follow `PEP8` style.
4. `annotations` function which is conflicting to same value in `__future__`
   is renamed to `reveal_annotations`.

And after updates of Python version and `mode-ng` itself, `ThreadService` is probably not stable yet for now.
Please carefully test your codes, if you're using it in production.

### Commits history

- [**breaking**] Update logging time format to timezone aware and format `extra` field in logger
- Make `want_seconds` raise `TypeError` when input is `None`
- Reorg cases for unit tests
- Update CoC guidelines and README
- [**breaking**] Improve logging module and setup args `loglevel` has been rename to `log_level`
- Improve implementations of singledispatch function
- Improve type hints for `signals.py` and reformat for `proxy.py`
- Fix circular imports and remove lazy importer
- Improve type hints for worker, services, etc
- [**breaking**] Remove `on_init` from now
- Improve notes for lazy loading
- Reconfig `.bumpversion.cfg`
- Tune flake8 config and adjust requirements content
- [**breaking**] Rename `annotations` to `reveal_annotations` due to conflict
- [**breaking**] Replace `Event` lock to std (asyncio) version. Need more tests in async tasks running in multiple threads.
- Remove `contexts.py` and improve type hints
- Adjust docs location about installation

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
