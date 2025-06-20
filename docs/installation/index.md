# Instalacja LLME

## 📦 Instalacja z PyPI

Najprostszym sposobem instalacji LLME jest użycie pip:

```bash
pip install emllm
```

## 📦 Instalacja z źródeł

1. Klonuj repozytorium:
```bash
git clone https://github.com/emllm/eml.git
cd eml
```

2. Zainstaluj zależności:
```bash
poetry install
```

## 🛠️ Wymagania systemowe

- **Python 3.8+** (standardowo dostępny)
- **Docker** (opcjonalnie, tylko dla komendy `run`)
- **Przeglądarka** (dowolna nowoczesna)

## 🔧 Zależności

- **FastAPI** - REST API framework
- **Pydantic** - walidacja danych
- **Pytest** - framework testowy
- **Black** - formatowanie kodu
- **Isort** - sortowanie importów
- **Flake8** - linting
- **Mypy** - sprawdzanie typów
- **Pdoc** - dokumentacja
