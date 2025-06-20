# FAQ

## 🛠️ Instalacja

### Jak zainstalować EMLLM z PyPI?
```bash
pip install emllm
```

### Jak zainstalować EMLLM z źródeł?
```bash
git clone https://github.com/emllm/eml.git
cd eml
poetry install
```

## 📱 Użycie

### Jak używać CLI?
```bash
emllm parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test"
```

### Jak używać REST API?
```python
import requests

response = requests.post(
    "http://localhost:8000/parse",
    json={"content": "From: test@example.com\nTo: recipient@example.com\nSubject: Test"}
)
```

## 🔍 API

### Jakie są dostępne endpointy REST API?
- `GET /health` - sprawdzenie statusu
- `POST /parse` - analiza wiadomości
- `POST /generate` - generowanie wiadomości
- `POST /validate` - walidacja wiadomości
- `POST /convert` - konwersja formatów

## 🛠️ Rozwiązywanie problemów

### Co zrobić, gdy występuje błąd walidacji?
Sprawdź, czy wiadomość zawiera wszystkie wymagane nagłówki:
- `From`
- `To`
- `Subject`

### Co zrobić, gdy REST API nie odpowiada?
1. Sprawdź, czy serwer jest uruchomiony
2. Sprawdź port (domyślnie 8000)
3. Sprawdź logi serwera
