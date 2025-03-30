.PHONY: format lint test test-integration test-all mypy ci init run validate requirements-install requirements-update list-sql coverage-view


# Requirements

requirements-install:
	pip install uv
	uv pip install -e '.[testing]'

requirements-update:
	uv pip install -U -e '.[testing]'
	@echo "Dependencies updated to latest versions"


# CI

format:
	ruff format src
	ruff format tests

lint:
	ruff check src
	ruff check tests

mypy:
	mypy src/speechdown

test:
	pytest tests/unit --cov=src/speechdown --cov-report term --cov-report html:coverage_html

test-integration:
	python -m pytest tests/integration -v --run-integration --run-slow

test-all:
	python -m pytest tests -v --run-integration --run-slow

ci: lint mypy test

ci-full: lint mypy test-all


# Development

reset:
	rm -rf tests/data/.speechdown

init:
	sd init -d tests/data

# also see tests/debug.py for debugging from VSCode
debug:
	sd transcribe -d tests/data --debug

debug-ignore-existing:
	sd transcribe -d tests/data --ignore-existing --debug

# SQL

list-sql:
	sqlite3 -header -column tests/data/.speechdown/speechdown.db < sql/list_transcriptions.sql

list-tables:
	sqlite3 -header -column tests/data/.speechdown/speechdown.db < sql/list_tables.sql

# Coverage

coverage-view:
	open coverage_html/index.html