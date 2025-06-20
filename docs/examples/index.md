# Przykłady użycia EMLLM

## 📝 Przykład podstawowy

```python
from emllm.core import emllmParser
from emllm.validator import emllmValidator

# Przykładowa wiadomość
emllm_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""

# Analiza
parser = emllmParser()
message = parser.parse(emllm_content)

# Konwersja do słownika
data = parser.to_dict(message)

# Walidacja
validator = emllmValidator()
validator.validate(data)
```

## 📡 Przykład z REST API

```python
import requests

# Analiza wiadomości
response = requests.post(
    "http://localhost:8888/parse",
    json={"content": "From: test@example.com\nTo: recipient@example.com\nSubject: Test"}
)

# Walidacja
response = requests.post(
    "http://localhost:8888/validate",
    json={"content": "From: test@example.com\nTo: recipient@example.com\nSubject: Test"}
)

# Konwersja
response = requests.post(
    "http://localhost:8888/convert",
    params={"from_format": "emllm", "to_format": "json"},
    json={"content": "From: test@example.com\nTo: recipient@example.com\nSubject: Test"}
)
```

## 📱 Przykład z CLI

```bash
# Analiza
emllm parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test"

# Walidacja
emllm validate "From: test@example.com\nTo: recipient@example.com\nSubject: Test"

# Konwersja
emllm convert --from emllm --to json "From: test@example.com\nTo: recipient@example.com\nSubject: Test"
```

## 📝 Przykład z załącznikami

```python
from emllm.core import emllmParser

# Wiadomość z załącznikiem
emllm_content = """
From: test@example.com
To: recipient@example.com
Subject: Test with attachment

Hello World

--attachment
Content-Type: text/plain
Content-Disposition: attachment; filename="example.txt"

This is an attachment
--
"""

parser = emllmParser()
message = parser.parse(emllm_content)
data = parser.to_dict(message)

# Dostęp do załącznika
data["attachments"]  # lista załączników
```
