# Project Makefile for PEML (Python Email Message Language)

# Project name
PROJECT_NAME = peml

# Poetry environment
POETRY := poetry

# Python paths
PYTHON := $(shell $(POETRY) env info --path)/bin/python

.PHONY: install test lint clean build publish docs start-server test-message

# Install dependencies and package
install:
	$(POETRY) install

# Run tests
.PHONY: test
test:
	$(PYTHON) -m pytest tests/

# Run linters
.PHONY: lint
lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check .

# Build package
.PHONY: build
build:
	$(POETRY) build

# Publish package to PyPI
.PHONY: publish
publish:
	$(POETRY) build
	$(POETRY) publish --build

# Generate documentation
.PHONY: docs
docs:
	$(PYTHON) -m pdoc --html --output-dir docs .

# Clean up
.PHONY: clean
clean:
	$(POETRY) env remove
	rm -rf .mypy_cache/ .pytest_cache/ .coverage/ .coverage.* coverage.xml htmlcov/ .cache/ .tox/ .venv/ .eggs/ *.egg-info/ dist/ build/ docs/

# Start REST server
.PHONY: start-server
start-server:
	$(PYTHON) -m peml.cli rest --host 0.0.0.0 --port 8000

# Test message parsing
.PHONY: test-message
test-message:
	$(PYTHON) -m peml.cli parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test\n\nHello World"
