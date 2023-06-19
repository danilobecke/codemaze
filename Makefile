setup: requirements.txt
	pip install -r requirements.txt
	chmod 777 hooks/pre-commit
	git config core.hooksPath hooks
run:
	python code/app.py
test:
	pytest --ignore=code/repository --cov-report term-missing:skip-covered --cov=code
code-coverage:
	pytest --ignore=code/repository --cov-report= --cov=code
	coverage-badge -f -o metadata/coverage.svg
clean:
	pyclean .
