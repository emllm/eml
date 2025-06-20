# Użycie EMLLM

## 📱 CLI

emllm oferuje interfejs wiersza poleceń (CLI) do pracy z wiadomościami email:

```bash
emllm parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test\n\nHello World"
```

Dostępne komendy:
- `parse` - analiza wiadomości email
- `generate` - generowanie wiadomości email
- `validate` - walidacja wiadomości
- `convert` - konwersja formatów
- `rest` - uruchomienie serwera REST

## 🌐 REST API

emllm udostępnia REST API na porcie 8000:

### Endpoints:

- `GET /health` - sprawdzenie statusu
- `POST /parse` - analiza wiadomości
- `POST /generate` - generowanie wiadomości
- `POST /validate` - walidacja wiadomości
- `POST /convert` - konwersja formatów

## 📝 Przykład użycia

```python
from emllm.core import emllmParser
from emllm.validator import emllmValidator

# Analiza wiadomości
parser = emllmParser()
message = parser.parse("From: test@example.com\nTo: recipient@example.com\nSubject: Test")

# Walidacja
validator = emllmValidator()
validator.validate(message)

# Konwersja do słownika
data = parser.to_dict(message)
```
