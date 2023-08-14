VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
COVERAGE_BADGE = $(VENV)/bin/coverage-badge
PYCLEAN = $(VENV)/bin/pyclean
PYLINT = $(VENV)/bin/pylint
MYPY = $(VENV)/bin/mypy

# setup, run, test, lint, type-ceck, and stop
setup: requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt
	chmod 777 scripts/pre-commit
	chmod 777 scripts/run_gcc_container_if_needed.sh
	chmod 777 scripts/stop_gcc_container.sh
	git config core.hooksPath scripts
	docker build -t gcc-image . 
run:
	./scripts/run_gcc_container_if_needed.sh
	$(PYTHON) code/app.py
test:
	./scripts/run_gcc_container_if_needed.sh
	$(PYTEST) --cov-report term-missing:skip-covered -c configs/pytest.ini
	$(COVERAGE_BADGE) -f -o metadata/coverage.svg
lint:
	$(PYLINT) code --rcfile=configs/.pylintrc
type-check:
	$(MYPY) code --config-file configs/mypy.ini
stop:
	./scripts/stop_gcc_container.sh

# pip install and freeze
add:
	$(PIP) install $(package)
freeze:
	$(PIP) freeze > requirements.txt

# pre-commit helpers
smoke-test:
	./scripts/run_gcc_container_if_needed.sh
	$(PYTEST) -c configs/pytest.ini --cov-report= -m smoke
lint-hook:
	$(PYLINT) --rcfile=configs/.pylintrc $(files)

# clear the cache and remove venv
clean:
	$(PYCLEAN) .
	rm -rf venv
