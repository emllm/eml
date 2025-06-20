# Python Email Message Language (PEML)

PEML is a Python library for working with email messages. It provides a simple interface for parsing, validating, and generating email messages.

## Features

- Parse email messages from text format
- Generate email messages from structured data
- Validate email message structure
- Convert between different formats
- Handle attachments
- REST API interface
- Command line interface

## Installation

You can install PEML using Poetry:

```bash
poetry install
```

Or directly from PyPI:

```bash
pip install peml
```

## Usage

### Command Line Interface

```bash
# Parse a message
peml parse "From: test@example.com\nTo: recipient@example.com\nSubject: Test\n\nHello World"

# Generate a message from JSON
peml generate --input message.json

# Validate a message
peml validate "From: test@example.com\nTo: recipient@example.com\nSubject: Test"

# Convert between formats
peml convert --from peml --to json --input message.peml --output message.json
```

### REST API

Start the REST server:

```bash
peml rest --host 0.0.0.0 --port 8000
```

Available endpoints:

- POST `/parse`: Parse a PEML message
- POST `/generate`: Generate a PEML message from structured data
- POST `/validate`: Validate a PEML message
- POST `/convert`: Convert between formats
- GET `/health`: Check server status

### Python API

```python
from peml.core import PEMLParser
from peml.validator import PEMLValidator

# Parse a message
parser = PEMLParser()
message = parser.parse("""
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
""")

# Validate a message
validator = PEMLValidator()
validator.validate({
    'headers': {
        'From': 'test@example.com',
        'To': 'recipient@example.com',
        'Subject': 'Test'
    },
    'body': 'Hello World',
    'attachments': []
})

# Convert to dictionary
message_dict = parser.to_dict(message)

# Generate from dictionary
new_message = parser.from_dict(message_dict)
```

## Message Structure

A valid PEML message must contain these required headers:
- From
- To
- Subject

It can also contain:
- Body content
- Attachments
- Additional headers

## Validation Rules

- All required headers must be present
- Email addresses must be valid
- Content types must be valid MIME types
- Attachments must have proper content type and filename

## License

MIT License
