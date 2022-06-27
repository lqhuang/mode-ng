PROJ ?= mode
PGPIDENT ?= "Lanqing Huang"
PYTHON ?= python
PYTEST ?= pytest
PIP ?= pip
GIT ?= git
TOX ?= tox
ICONV ?= iconv
FLAKE8 ?= flake8
PYDOCSTYLE ?= pydocstyle
MYPY ?= mypy
SPHINX2RST ?= sphinx2rst
BUMPVERSION ?= bumpversion

TESTDIR ?= tests
SPHINX_DIR ?= docs/
SPHINX_BUILDDIR ?= "${SPHINX_DIR}/_build"
README ?= README.rst
README_SRC ?= "docs/templates/readme.txt"
CONTRIBUTING ?= CONTRIBUTING.rst
CONTRIBUTING_SRC ?= "docs/contributing.rst"
COC ?= CODE_OF_CONDUCT.rst
COC_SRC ?= "docs/includes/code-of-conduct.txt"
SPHINX_HTMLDIR="${SPHINX_BUILDDIR}/html"
DOCUMENTATION=Documentation

all: help

help:
	@echo "docs                 - Build documentation."
	@echo "test-all             - Run tests for all supported python versions."
	@echo "develop              - Install all dependencies into current virtualenv."
	@echo "distcheck ---------- - Check distribution for problems."
	@echo "  test               - Run unittests using current python."
	@echo "  lint ------------  - Check codebase for problems."
	@echo "    apicheck         - Check API reference coverage."
	@echo "    readmecheck      - Check README.rst encoding."
	@echo "    contribcheck     - Check CONTRIBUTING.rst encoding"
	@echo "    flakes --------  - Check code for syntax and style errors."
	@echo "      typecheck      - Run the mypy type checker"
	@echo "      flakecheck     - Run flake8 on the source code."
	@echo "      pep257check    - Run pep257 on the source code."
	@echo "readme               - Regenerate README.rst file."
	@echo "contrib              - Regenerate CONTRIBUTING.rst file"
	@echo "coc                  - Regenerate CODE_OF_CONDUCT.rst file"
	@echo "clean-dist --------- - Clean all distribution build artifacts."
	@echo "  clean-git-force    - Remove all uncomitted files."
	@echo "  clean ------------ - Non-destructive clean"
	@echo "    clean-pyc        - Remove .pyc/__pycache__ files"
	@echo "    clean-docs       - Remove documentation build artifacts."
	@echo "    clean-build      - Remove setup artifacts."
	@echo "bump                 - Bump patch version number."
	@echo "bump-minor           - Bump minor version number."
	@echo "bump-major           - Bump major version number."
	@echo "release              - Make PyPI release."

clean: clean-docs clean-pyc clean-build

clean-dist: clean clean-git-force

. PHONY: Documentation
Documentation:
	$(PIP) install -r requirements/docs.txt
	(cd "$(SPHINX_DIR)"; $(MAKE) html)
	mv "$(SPHINX_HTMLDIR)" $(DOCUMENTATION)

. PHONY: docs
docs: Documentation

clean-docs:
	-rm -rf "$(SPHINX_BUILDDIR)"

lint: flakecheck apicheck readmecheck

apicheck:
	(cd "$(SPHINX_DIR)"; $(MAKE) apicheck)

flakecheck:
	$(FLAKE8) "$(PROJ)" "$(TESTDIR)" examples/

pep257check:
	$(PYDOCSTYLE) "$(PROJ)"

flakediag:
	-$(MAKE) flakecheck

flakes: flakediag

clean-readme:
	-rm -f $(README)

readmecheck:
	$(ICONV) -f ascii -t ascii $(README) >/dev/null

$(README):
	$(SPHINX2RST) "$(README_SRC)" --ascii > $@

readme: clean-readme $(README) readmecheck

clean-contrib:
	-rm -f "$(CONTRIBUTING)"

$(CONTRIBUTING):
	$(SPHINX2RST) "$(CONTRIBUTING_SRC)" > $@

contrib: clean-contrib $(CONTRIBUTING)

clean-coc:
	-rm -f "$(COC)"

$(COC):
	$(SPHINX2RST) "$(COC_SRC)" > $@

coc: clean-coc $(COC)

clean-pyc:
	-find . -type f -a \( -name "*.pyc" -o -name "*$$py.class" \) | xargs rm
	-find . -type d -name "__pycache__" | xargs rm -r

removepyc: clean-pyc

clean-git:
	$(GIT) clean -xdn

clean-git-force:
	$(GIT) clean -xdf

test-all: clean-pyc
	$(TOX)

test:
	$(PYTEST) .

cov:
	$(PYTEST) -x --cov="$(PROJ)" --cov-report=html

distcheck: lint test clean

dist: readme contrib clean-dist build

typecheck:
	$(MYPY) --pretty -p $(PROJ)


# ------------------------- Dev setup ----------------------------------------
. PHONY: venv
venv:
	${PYTHON} -m venv .venv --clear

. PHONY: deps-default
deps-default:
	$(PIP) install -U -r requirements/default.txt

. PHONY: deps-dist
deps-dist:
	$(PIP) install -U -r requirements/dist.txt

. PHONY: deps-docs
deps-docs:
	$(PIP) install -U -r requirements/docs.txt

. PHONY: deps-test
deps-test:
	$(PIP) install -U -r requirements/test.txt

. PHONY: deps-typecheck
deps-typecheck:
	$(PIP) install -U -r requirements/typecheck.txt

. PHONY: deps-extras
deps-extras:
	$(PIP) install -U -r requirements/extras/eventlet.txt
	$(PIP) install -U -r requirements/extras/uvloop.txt

. PHONY: develop
develop: deps-default deps-dist deps-docs deps-test deps-typecheck deps-extras
	$(PYTHON) setup.py develop

.PHONY: requirements
requirements:
	$(PIP) install --upgrade pip
	for f in `ls requirements/` ; do $(PIP) install -r requirements/$$f ; done

.PHONY: clean-requirements
clean-requirements:
	pip freeze | xargs pip uninstall -y
	$(MAKE) requirements


# ---------------------- Release distribution --------------------------------
bump:
	${BUMPVERSION} patch

bump-minor:
	${BUMPVERSION} minor

bump-major:
	${BUMPVERSION} major

do-build:
	${PYTHON} -m build -s -w

clean-build:
	rm -rf build/ .eggs/ *.egg-info/ .tox/ .coverage/ cover/

.PHONY: build
build: clean-build do-build

release:
	${PYTHON} -m twine check dist/*
	${PYTHON} -m twine upload --skip-existing dist/*
