.PHONY: format lint test test-integration test-all mypy ci init run validate requirements-install requirements-update

format:
	ruff format src
	ruff format tests

lint:
	ruff check src
	ruff check tests

test:
	pytest tests/unit

test-integration:
	python -m pytest tests/integration -v --run-integration --run-slow

test-all:
	python -m pytest tests -v --run-integration --run-slow

mypy:
	mypy src/speechdown

ci: lint mypy test

init:
	sd init -d tests/data

run:
	sd transcribe -d tests/data --dry-run --debug

# also see tests/validate.py
validate:
	sd transcribe -d tests/data

requirements-install:
	pip install uv
	uv pip install -e '.[testing]'

requirements-update:
	uv pip freeze > requirements.txt
	@echo "Dependencies updated in requirements.txt"