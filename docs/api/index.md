# API LLME

## 📚 Moduły

### Core

```python
class PEMLParser:
    def parse(self, peml_content: str) -> EmailMessage:
        """Analiza wiadomości PEML"""
    
    def to_dict(self, message: EmailMessage) -> Dict[str, Any]:
        """Konwersja do słownika"""
    
    def from_dict(self, data: Dict[str, Any]) -> EmailMessage:
        """Konwersja ze słownika"""

### Validator

```python
class PEMLValidator:
    def validate(self, data: Dict[str, Any]) -> None:
        """Walidacja wiadomości"""

### CLI

```python
class PEMLCLI:
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
Body: {"content": "PEML content"}

# /generate
POST /generate
Body: {
    "message": {"headers": {...}, "body": "..."},
    "validate": true
}

# /validate
POST /validate
Body: {"content": "PEML content"}

# /convert
POST /convert?from_format=peml&to_format=json
Body: {"content": "PEML content"}
```
