# Architektura emllm

## 🏗️ Struktura projektu

```
emllm/
├── src/
│   └── emllm/
│       ├── __init__.py
│       ├── api.py
│       ├── core.py
│       ├── cli.py
│       └── validator.py
├── tests/
│   ├── test_core.py
│   ├── test_validator.py
│   ├── test_cli.py
│   └── test_api.py
├── docs/
├── pyproject.toml
├── Makefile
└── README.md
```

## 📚 Moduły

### Core

- `emllmParser`: analiza i konwersja wiadomości
- `emllmValidator`: walidacja wiadomości

### API

- REST API z FastAPI
- Pydantic models
- Walidacja żądań

### CLI

- Interfejs wiersza poleceń
- Obsługa komend
- Walidacja argumentów

## 🔄 Workflow

1. **Wejście**: Wiadomość emllm lub JSON
2. **Analiza**: emllmParser
3. **Walidacja**: emllmValidator
4. **Konwersja**: emllmParser
5. **Wyjście**: Wiadomość emllm lub JSON

## 🔧 Konfiguracja

- Pyproject.toml: konfiguracja Poetry
- Makefile: zadania deweloperskie
- .gitignore: ignorowane pliki
