.PHONY: format lint test test-integration test-all mypy ci init run validate requirements-install requirements-update

format:
	ruff format src
	ruff format tests

lint:
	ruff check src
	ruff check tests

mypy:
	mypy src/speechdown

test:
	pytest tests/unit

test-integration:
	python -m pytest tests/integration -v --run-integration --run-slow

test-all:
	python -m pytest tests -v --run-integration --run-slow

ci: lint mypy test

ci-full: lint mypy test-all

init:
	sd init -d tests/data

run:
	sd transcribe -d tests/data --dry-run --debug

# also see tests/debug.py for debugging from VSCode
debug:
	sd transcribe -d tests/data --debug

requirements-install:
	pip install uv
	uv pip install -e '.[testing]'

requirements-update:
	uv pip freeze > requirements.txt
	@echo "Dependencies updated in requirements.txt"