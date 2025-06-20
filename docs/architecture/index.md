# Architektura LLME

## 🏗️ Struktura projektu

```
llme/
├── src/
│   └── llme/
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

- `PEMLParser`: analiza i konwersja wiadomości
- `PEMLValidator`: walidacja wiadomości

### API

- REST API z FastAPI
- Pydantic models
- Walidacja żądań

### CLI

- Interfejs wiersza poleceń
- Obsługa komend
- Walidacja argumentów

## 🔄 Workflow

1. **Wejście**: Wiadomość PEML lub JSON
2. **Analiza**: PEMLParser
3. **Walidacja**: PEMLValidator
4. **Konwersja**: PEMLParser
5. **Wyjście**: Wiadomość PEML lub JSON

## 🔧 Konfiguracja

- Pyproject.toml: konfiguracja Poetry
- Makefile: zadania deweloperskie
- .gitignore: ignorowane pliki
