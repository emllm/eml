# API emllm

## 📚 Moduły

### Core

```python
class emllmParser:
    def parse(self, emllm_content: str) -> EmailMessage:
        """Analiza wiadomości emllm"""
    
    def to_dict(self, message: EmailMessage) -> Dict[str, Any]:
        """Konwersja do słownika"""
    
    def from_dict(self, data: Dict[str, Any]) -> EmailMessage:
        """Konwersja ze słownika"""

### Validator

```python
class emllmValidator:
    def validate(self, data: Dict[str, Any]) -> None:
        """Walidacja wiadomości"""

### CLI

```python
class emllmCLI:
    def parse(self, content: str) -> str:
        """Analiza wiadomości"""
    
    def generate(self, data: Dict[str, Any]) -> str:
        """Generowanie wiadomości"""
    
    def validate(self, content: str) -> None:
        """Walidacja wiadomości"""
    
    def convert(self, content: str, from_format: str, to_format: str) -> str:
        """Konwersja formatów"""

## 📡 REST API

### Endpoints

```python
# /health
GET /health

# /parse
POST /parse
Body: {"content": "emllm content"}

# /generate
POST /generate
Body: {
    "message": {"headers": {...}, "body": "..."},
    "validate": true
}

# /validate
POST /validate
Body: {"content": "emllm content"}

# /convert
POST /convert?from_format=emllm&to_format=json
Body: {"content": "emllm content"}
```
