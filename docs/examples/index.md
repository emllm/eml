# Przykłady użycia LLME

## 📝 Przykład podstawowy

```python
from llme.core import PEMLParser
from llme.validator import PEMLValidator

# Przykładowa wiadomość
peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""

# Analiza
parser = PEMLParser()
message = parser.parse(peml_content)

# Konwersja do słownika
data = parser.to_dict(message)

# Walidacja
validator = PEMLValidator()
validator.validate(data)
```

## 📡 Przykład z REST API

```python
import requests

# Analiza wiadomości
response = requests.post(
    "http://localhost:8000/parse",
    json={"content": "From: test@example.com\nTo: recipient@example.com\nSubject: Test"}
)

# Walidacja
response = requests.post(
    "http://localhost:8000/validate",
    json={"content": "From: test@example.com\nTo: recipient@example.com\nSubject: Test"}
)

# Konwersja
response = requests.post(
    "http://localhost:8000/convert",
    params={"from_format": "peml", "to_format": "json"},
    json={"content": "From: test@example.com\nTo: recipient@example.com\nSubject: Test"}
)
```

## 📱 Przykład z CLI

```bash
# Analiza
llme parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test"

# Walidacja
llme validate "From: test@example.com\nTo: recipient@example.com\nSubject: Test"

# Konwersja
llme convert --from peml --to json "From: test@example.com\nTo: recipient@example.com\nSubject: Test"
```

## 📝 Przykład z załącznikami

```python
from llme.core import PEMLParser

# Wiadomość z załącznikiem
peml_content = """
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

parser = PEMLParser()
message = parser.parse(peml_content)
data = parser.to_dict(message)

# Dostęp do załącznika
data["attachments"]  # lista załączników
```
