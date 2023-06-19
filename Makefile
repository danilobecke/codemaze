setup: requirements.txt
	pip install -r requirements.txt
run:
	python code/app.py
test:
	pytest --ignore=code/repository
