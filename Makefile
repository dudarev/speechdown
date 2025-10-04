.PHONY: ai-rules check-ffmpeg ci ci-full coverage-view debug debug-ignore-existing format init install-dev lint list-sql list-tables mypy requirements requirements-update reset run test test-all test-integration validate logo

clean:
	rm -rf tests/data/transcripts
	rm -rf .coverage*

# Requirements

check-ffmpeg:
	@if ! command -v ffmpeg > /dev/null 2>&1; then \
		if [[ "$$(uname)" == "Darwin" ]]; then \
			echo "ffmpeg not found. Installing via Homebrew..."; \
			brew install ffmpeg; \
		else \
			echo "ffmpeg not found. Please install ffmpeg for your system."; \
			exit 1; \
		fi; \
	else \
		echo "ffmpeg is already installed."; \
	fi

requirements: check-ffmpeg
	pip install uv
	uv pip install -e '.[testing]'

install-global:
	@echo "Installing SpeechDown globally using uvx..."
	@if ! command -v uv > /dev/null 2>&1; then \
		echo "uv not found. Installing via pip..."; \
		pip install uv; \
	fi
	uvx --from git+https://github.com/dudarev/speechdown sd --help
	@echo "SpeechDown installed globally. Run 'sd --help' to verify."

requirements-local:
	uv pip install -e '.[testing-local]'
	@echo "Local development environment set up with dependencies"

requirements-update:
	uv pip install -U -e '.[testing-local]'
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
	pytest tests/unit

test-integration:
	python -m pytest tests/integration -v --run-integration --run-slow

test-all:
	python -m pytest tests -v --run-integration --run-slow --cov=src/speechdown --cov-report term --cov-report html:coverage_html

# Used in GitHub CI and for remote AI assistants
ci: lint mypy test test-integration

# Used in local CI and for local AI assistants
ci-local: lint mypy test-all


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

# AI Assistants

ai-rules:
	@echo "Generating AI assistant rule files from master AI-rules.md..."
	@python scripts/generate_ai_rules.py docs/ai/AI-rules.md
	@echo "AI rule files generated successfully."

# Graphics
svg_logo := graphics/logo.svg
png_logo := graphics/logo.png
logo:
	@if [ ! -f "$(svg_logo)" ]; then \
		echo "SVG logo file not found: $(svg_logo)"; \
		exit 1; \
	fi
	@echo "Converting $(svg_logo) to graphics/temp.png with width 1024 using Inkscape..."
	inkscape $(svg_logo) --export-type=png --export-width=1024 --export-filename=graphics/temp.png || \
		inkscape $(svg_logo) --export-type=png --export-height=1024 --export-filename=graphics/temp.png
	@echo "Padding graphics/temp.png to 1024x1024 using ImageMagick..."
	convert graphics/temp.png -gravity center -background none -extent 1024x1024 $(png_logo)
	@rm -f graphics/temp.png
	@echo "Done: $(png_logo)"
