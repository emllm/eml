# Konfiguracja EMLLM

## 🛠️ Pyproject.toml

```toml
[tool.poetry]
name = "emllm"
version = "0.1.1"
description = "Large Language Model Email Message registry and interpreter"
authors = ["Tom Sapletta <info@softreck.dev>"]
packages = [{include = "emllm", from = "src"}]

[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.104.1"
uvicorn = "^0.24.0"
pydantic = "^2.4.2"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-cov = "^4.1.0"
black = "^23.11.0"
isort = "^5.12.0"
flake8 = "^6.1.0"
mypy = "^1.6.1"
pdoc = "^13.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
emllm = "emllm.cli:main"
```

## 📝 Makefile

```makefile
# Project Makefile for emllm

# Project name
PROJECT_NAME = emllm

# Poetry environment
POETRY := poetry

# Python paths
PYTHON := $(shell $(POETRY) env info --path)/bin/python
PYTHON_SRC := src/$(PROJECT_NAME)

.PHONY: install
distclean:
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/

.PHONY: build
build:
	$(POETRY) build

.PHONY: publish
publish:
	$(POETRY) build
	$(POETRY) publish --build --no-interaction

.PHONY: docs
docs:
	pdoc --html --output-dir docs/html src/emllm

.PHONY: test
test:
	$(PYTHON) -m pytest tests/ --cov=$(PYTHON_SRC) --cov-report=term-missing

.PHONY: lint
lint:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	$(PYTHON) -m flake8 .

.PHONY: type-check
type-check:
	$(PYTHON) -m mypy .

.PHONY: clean
clean:
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
```
