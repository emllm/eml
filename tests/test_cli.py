import pytest
import subprocess
import json
import os

def test_cli_parse():
    result = subprocess.run(
        [
            "python", "-m", "peml.cli", "parse",
            "From: test@example.com\nTo: recipient@example.com\nSubject: Test\n\nHello World"
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "From: test@example.com" in result.stdout
    assert "To: recipient@example.com" in result.stdout
    assert "Subject: Test" in result.stdout
    assert "Hello World" in result.stdout

def test_cli_generate(tmp_path):
    # Create a test JSON file
    test_json = {
        "headers": {
            "From": "test@example.com",
            "To": "recipient@example.com",
            "Subject": "Test"
        },
        "body": "Hello World",
        "attachments": []
    }
    
    json_path = tmp_path / "test.json"
    with open(json_path, "w") as f:
        json.dump(test_json, f)
    
    # Run the generate command
    result = subprocess.run(
        ["python", "-m", "peml.cli", "generate", "--input", str(json_path)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "From: test@example.com" in result.stdout
    assert "To: recipient@example.com" in result.stdout
    assert "Subject: Test" in result.stdout
    assert "Hello World" in result.stdout

def test_cli_validate():
    result = subprocess.run(
        [
            "python", "-m", "peml.cli", "validate",
            "From: test@example.com\nTo: recipient@example.com\nSubject: Test"
        ],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Message is valid!" in result.stdout

def test_cli_convert(tmp_path):
    # Create a test PEML file
    peml_content = """
From: test@example.com
To: recipient@example.com
Subject: Test

Hello World
"""
    
    peml_path = tmp_path / "test.peml"
    json_path = tmp_path / "test.json"
    
    with open(peml_path, "w") as f:
        f.write(peml_content)
    
    # Convert PEML to JSON
    result = subprocess.run(
        [
            "python", "-m", "peml.cli", "convert",
            "--from", "peml",
            "--to", "json",
            "--input", str(peml_path),
            "--output", str(json_path)
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert os.path.exists(json_path)
    
    # Verify the JSON output
    with open(json_path) as f:
        data = json.load(f)
        assert data["headers"]["From"] == "test@example.com"
        assert data["headers"]["To"] == "recipient@example.com"
        assert data["headers"]["Subject"] == "Test"
        assert data["body"] == "Hello World"
