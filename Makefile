VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
COVERAGE_BADGE = $(VENV)/bin/coverage-badge
PYCLEAN = $(VENV)/bin/pyclean

setup: requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt
	chmod 777 hooks/pre-commit
	git config core.hooksPath hooks
run:
	$(PYTHON) code/app.py
test:
	$(PYTEST) --ignore=code/repository --cov-report term-missing:skip-covered --cov=code
code-coverage:
	$(PYTEST) --ignore=code/repository --cov-report= --cov=code
	$(COVERAGE_BADGE) -f -o metadata/coverage.svg
clean:
	$(PYCLEAN) .
	rm -rf venv
