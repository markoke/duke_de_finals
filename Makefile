install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

# format:
# 	black *.py # Databricks conflicts

lint:
	ruff check app/*.py
