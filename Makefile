VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
COVERAGE_BADGE = $(VENV)/bin/coverage-badge
PYCLEAN = $(VENV)/bin/pyclean
PYLINT = $(VENV)/bin/pylint
MYPY = $(VENV)/bin/mypy

# setup, run, test, and lint
setup: requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt
	chmod 777 hooks/pre-commit
	git config core.hooksPath hooks
run:
	$(PYTHON) code/app.py
test:
	$(PYTEST) --ignore=code/repository --cov-report term-missing:skip-covered --cov-config=configs/.coveragerc --cov=code
lint:
	$(PYLINT) code --rcfile=configs/.pylintrc
type-check:
	$(MYPY) code --config-file configs/mypy.ini --check-untyped-defs --disallow-untyped-calls

# pip install and freeze
add:
	$(PIP) install $(package)
freeze:
	$(PIP) freeze > requirements.txt

# pre-commit helpers
code-coverage:
	$(PYTEST) --ignore=code/repository --cov-report= --cov-config=configs/.coveragerc --cov=code
	$(COVERAGE_BADGE) -f -o metadata/coverage.svg
lint-hook:
	$(PYLINT) --rcfile=configs/.pylintrc $(files)

# clear the cache and remove venv
clean:
	$(PYCLEAN) .
	rm -rf venv
