# Python EML Self-Extracting Script

This directory contains a Python implementation of a self-extracting EML script that combines an email message with an embedded web application.

## File: `testapp.eml.py`

### Description
`testapp.eml.py` is a self-extracting script that combines an email message with an embedded web application. The file is both:
1. An executable Python script
2. A valid EML file with attachments

### Features
- Cross-platform support (Windows, macOS, Linux)
- Multiple execution modes (extract, run, browse, info)
- Automatic HTML content extraction
- Docker support for containerized execution
- Interactive GUI for Windows (when double-clicked)

### Requirements
- Python 3.6 or higher
- Standard Python libraries (no external dependencies required)
- Docker (for containerized execution)

### Usage
```bash
# Make the script executable (Linux/macOS)
chmod +x testapp.eml.py

# Run with options:
./testapp.eml.py [command]

Available commands:
- extract - Extract content to a directory
- run     - Run the application in a Docker container
- browse  - Open in default web browser (default)
- info    - Show script information
- help    - Show help message
```

### Examples
```bash
# Extract content to a directory
./testapp.eml.py extract

# Run in a Docker container
./testapp.eml.py run

# Open in default browser
./testapp.eml.py browse

# Show script information
./testapp.eml.py info
```

### How It Works
1. The script contains both Python code and EML content
2. When executed, it extracts the embedded web application
3. It can run the application in different modes:
   - Directly in a web browser
   - In a Docker container
   - Extract files to a directory

### File Structure
- `testapp.eml.py` - Main script file containing both code and content
- Extracted files are stored in a temporary directory when run

### Differences from Shell Version
- Written in Python instead of Bash
- Better cross-platform compatibility
- More robust error handling
- Additional features like Docker support
- Interactive GUI on Windows

### Notes
- The script is designed to be both executable and a valid EML file
- It can be sent as an email attachment and still work when downloaded and executed
- The embedded web application is a simple dashboard for invoice management
