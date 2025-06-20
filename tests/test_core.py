import pytest
from .peml.core import PEMLParser, PEMLError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

def test_parse_simple_message():
    peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""
    parser = PEMLParser()
    message = parser.parse(peml_content)
    
    assert message['From'] == 'test@example.com'
    assert message['To'] == 'recipient@example.com'
    assert message['Subject'] == 'Test'
    assert message.get_body().get_content() == 'Hello World'

def test_parse_message_with_attachment():
    peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test with attachment

This is a test message

--boundary
Content-Type: text/plain
Content-Disposition: attachment; filename="test.txt"

Hello World
--boundary--
"""
    parser = PEMLParser()
    message = parser.parse(peml_content)
    
    assert len(list(message.iter_attachments())) == 1
    attachment = next(message.iter_attachments())
    assert attachment.get_filename() == 'test.txt'
    assert attachment.get_content() == 'Hello World'

def test_parse_invalid_message():
    parser = PEMLParser()
    with pytest.raises(PEMLError):
        parser.parse("Invalid message format")

def test_to_dict_conversion():
    peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""
    parser = PEMLParser()
    message = parser.parse(peml_content)
    result = parser.to_dict(message)
    
    assert result['headers']['From'] == 'test@example.com'
    assert result['headers']['To'] == 'recipient@example.com'
    assert result['headers']['Subject'] == 'Test'
    assert result['body'] == 'Hello World'
    assert result['attachments'] == []

def test_from_dict_conversion():
    data = {
        'headers': {
            'From': 'test@example.com',
            'To': 'recipient@example.com',
            'Subject': 'Test'
        },
        'body': 'Hello World',
        'attachments': []
    }
    
    parser = PEMLParser()
    message = parser.from_dict(data)
    
    assert message['From'] == 'test@example.com'
    assert message['To'] == 'recipient@example.com'
    assert message['Subject'] == 'Test'
    assert message.get_body().get_content() == 'Hello World'

def test_round_trip_conversion():
    peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""
    parser = PEMLParser()
    message = parser.parse(peml_content)
    
    # Convert to dict and back
    data = parser.to_dict(message)
    new_message = parser.from_dict(data)
    
    assert new_message.as_string() == message.as_string()
