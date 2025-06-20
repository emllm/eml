# FAQ

## 🛠️ Instalacja

### Jak zainstalować LLME z PyPI?
```bash
pip install llme
```

### Jak zainstalować LLME z źródeł?
```bash
git clone https://github.com/tomsapletta/llme.git
cd llme
poetry install
```

## 📱 Użycie

### Jak używać CLI?
```bash
llme parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test"
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
