VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
COVERAGE_BADGE = $(VENV)/bin/coverage-badge
PYCLEAN = $(VENV)/bin/pyclean

# setup, run, and test
setup: requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt
	chmod 777 hooks/pre-commit
	git config core.hooksPath hooks
run:
	$(PYTHON) code/app.py
test:
	$(PYTEST) --ignore=code/repository --cov-report term-missing:skip-covered --cov-config=configs/.coveragerc --cov=code

# pip install and freeze
add:
	$(PIP) install $(package)
freeze:
	$(PIP) freeze > requirements.txt

# pre-commit helpers
code-coverage:
	$(PYTEST) --ignore=code/repository --cov-report= --cov-config=configs/.coveragerc --cov=code
	$(COVERAGE_BADGE) -f -o metadata/coverage.svg
# clear the cache and remove venv
clean:
	$(PYCLEAN) .
	rm -rf venv
