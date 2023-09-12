VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
COVERAGE_BADGE = $(VENV)/bin/coverage-badge
PYCLEAN = $(VENV)/bin/pyclean
PYLINT = $(VENV)/bin/pylint
MYPY = $(VENV)/bin/mypy
PIPREMOVE = $(VENV)/bin/pip-autoremove

# deploy
build:
	./scripts/create_dot_env.sh deploy
	docker compose -f compose.yaml -f compose.deploy.yaml build
deploy:
	docker compose -f compose.yaml -f compose.deploy.yaml up -d
stop-deploy:
	docker compose -f compose.yaml -f compose.deploy.yaml down

# setup
setup: requirements.txt, build-test
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt
	chmod 777 scripts/pre-commit
	chmod 777 scripts/create_dot_env.sh
	git config core.hooksPath scripts

# test (setup, up, test, stop)
build-test:
	./scripts/create_dot_env.sh test
	docker compose -f compose.yaml -f compose.test.yaml build
up-test:
	./scripts/create_dot_env.sh test
	docker compose -f compose.yaml -f compose.test.yaml up -d
test: up-test
	$(PYTEST) --cov-report term-missing:skip-covered -c configs/pytest.ini
	$(COVERAGE_BADGE) -f -o metadata/coverage.svg
stop-test:
	docker compose -f compose.yaml -f compose.test.yaml down

# debug (setup, up, debug, stop)
build-debug:
	./scripts/create_dot_env.sh debug
	docker compose -f compose.yaml -f compose.debug.yaml build	
debug:
	docker compose -f compose.yaml -f compose.debug.yaml up
stop-debug:
	docker compose -f compose.yaml -f compose.debug.yaml down

# lint and type-check
lint:
	$(PYLINT) code --rcfile=configs/.pylintrc
type-check:
	$(MYPY) code --config-file configs/mypy.ini

# pip install, freeze, and remove
add:
	$(PIP) install $(package)
freeze:
	$(PIP) freeze > requirements.txt
remove:
	$(PIPREMOVE) $(package) -y

# pre-commit helpers
smoke-test: up-test
	$(PYTEST) -c configs/pytest.ini --cov-report= -m smoke
lint-hook:
	$(PYLINT) --rcfile=configs/.pylintrc $(files)

# clear the cache and remove venv
clean:
	$(PYCLEAN) .
	rm -rf venv
