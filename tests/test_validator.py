import pytest
from .peml.validator import PEMLValidator

def test_valid_message():
    validator = PEMLValidator()
    data = {
        'headers': {
            'From': 'test@example.com',
            'To': 'recipient@example.com',
            'Subject': 'Test'
        },
        'body': 'Hello World',
        'attachments': []
    }
    validator.validate(data)

def test_missing_required_header():
    validator = PEMLValidator()
    data = {
        'headers': {
            'From': 'test@example.com',
            'Subject': 'Test'
        },
        'body': 'Hello World',
        'attachments': []
    }
    
    with pytest.raises(ValueError) as exc_info:
        validator.validate(data)
    assert 'Missing required header: To' in str(exc_info.value)

def test_invalid_email_address():
    validator = PEMLValidator()
    data = {
        'headers': {
            'From': 'invalid-email',
            'To': 'recipient@example.com',
            'Subject': 'Test'
        },
        'body': 'Hello World',
        'attachments': []
    }
    
    with pytest.raises(ValueError) as exc_info:
        validator.validate(data)
    assert 'Invalid email address in From' in str(exc_info.value)

def test_invalid_content_type():
    validator = PEMLValidator()
    data = {
        'headers': {
            'From': 'test@example.com',
            'To': 'recipient@example.com',
            'Subject': 'Test'
        },
        'body': 'Hello World',
        'attachments': [
            {
                'content_type': 'invalid/type',
                'filename': 'test.txt'
            }
        ]
    }
    
    with pytest.raises(ValueError) as exc_info:
        validator.validate(data)
    assert 'Invalid content_type' in str(exc_info.value)

def test_missing_content_type():
    validator = PEMLValidator()
    data = {
        'headers': {
            'From': 'test@example.com',
            'To': 'recipient@example.com',
            'Subject': 'Test'
        },
        'body': 'Hello World',
        'attachments': [
            {
                'filename': 'test.txt'
            }
        ]
    }
    
    with pytest.raises(ValueError) as exc_info:
        validator.validate(data)
    assert 'Missing content_type' in str(exc_info.value)
