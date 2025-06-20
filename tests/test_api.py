import pytest
import json
from fastapi.testclient import TestClient
from .api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}

def test_parse_valid_message():
    peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""
    
    response = client.post(
        "/parse",
        json={"content": peml_content}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    data = json.loads(result["message"])
    assert data["headers"]["From"] == "test@example.com"
    assert data["headers"]["To"] == "recipient@example.com"
    assert data["headers"]["Subject"] == "Test"
    assert data["body"] == "Hello World"

def test_parse_invalid_message():
    response = client.post(
        "/parse",
        json={"content": "Invalid message"}
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_generate_valid_message():
    message_data = {
        "message": {
            "headers": {
                "From": "test@example.com",
                "To": "recipient@example.com",
                "Subject": "Test"
            },
            "body": "Hello World",
            "attachments": []
        },
        "validate": True
    }
    
    response = client.post(
        "/generate",
        json=message_data
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "From: test@example.com" in result["message"]
    assert "To: recipient@example.com" in result["message"]
    assert "Subject: Test" in result["message"]
    assert "Hello World" in result["message"]

def test_generate_invalid_message():
    message_data = {
        "message": {
            "headers": {
                "From": "invalid-email",
                "To": "recipient@example.com",
                "Subject": "Test"
            },
            "body": "Hello World",
            "attachments": []
        },
        "validate": True
    }
    
    response = client.post(
        "/generate",
        json=message_data
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_convert_peml_to_json():
    peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""
    
    response = client.post(
        "/convert",
        params={
            "from_format": "peml",
            "to_format": "json"
        },
        json={"content": peml_content}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    data = json.loads(result["result"])
    assert data["headers"]["From"] == "test@example.com"
    assert data["headers"]["To"] == "recipient@example.com"
    assert data["headers"]["Subject"] == "Test"
    assert data["body"] == "Hello World"

def test_convert_json_to_peml():
    json_content = {
        "headers": {
            "From": "test@example.com",
            "To": "recipient@example.com",
            "Subject": "Test"
        },
        "body": "Hello World",
        "attachments": []
    }
    
    response = client.post(
        "/convert",
        params={
            "from_format": "json",
            "to_format": "peml"
        },
        json={"content": json_content}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    assert "From: test@example.com" in result["result"]
    assert "To: recipient@example.com" in result["result"]
    assert "Subject: Test" in result["result"]
    assert "Hello World" in result["result"]
