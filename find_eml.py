#!/usr/bin/env python3
# Script to help find EML content in a file

import sys
import re

def find_eml_content(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    
    print(f"Analyzing file: {filename}")
    print(f"File size: {len(content)} bytes")
    
    # Look for MIME headers
    mime_headers = [
        b'MIME-Version:',
        b'Content-Type:',
        b'Content-Transfer-Encoding:',
        b'From:',
        b'To:',
        b'Subject:'
    ]
    
    print("\nLooking for MIME headers...")
    for header in mime_headers:
        pos = content.find(header)
        if pos != -1:
            print(f"Found '{header.decode('latin-1')}' at position {pos}")
    
    # Look for boundaries
    print("\nLooking for boundaries...")
    boundary_pattern = rb'boundary=["\']?([^"\'\s;]+)'
    boundaries = re.finditer(boundary_pattern, content, re.IGNORECASE)
    for i, match in enumerate(boundaries):
        boundary = match.group(1)
        print(f"Found boundary: {boundary.decode('latin-1', errors='replace')} at position {match.start()}")
    
    # Look for potential base64 content
    print("\nLooking for base64 content...")
    base64_pattern = rb'[A-Za-z0-9+/=]{40,}'
    base64_matches = list(re.finditer(base64_pattern, content))
    if base64_matches:
        print(f"Found {len(base64_matches)} potential base64 chunks")
        for i, match in enumerate(base64_matches[:3]):  # Show first 3 matches
            print(f"  Match {i+1} at position {match.start()}, length: {len(match.group(0))}")
    
    # Look for the boundary marker we know about
    boundary = b'--UNIVERSAL_WEBAPP_BOUNDARY--'
    pos = content.rfind(boundary)
    if pos != -1:
        print(f"\nFound boundary marker at position {pos}")
        print(f"Content after boundary (first 200 bytes):")
        preview = content[pos+len(boundary):pos+len(boundary)+200]
        try:
            print(preview.decode('utf-8', errors='replace'))
        except:
            print("Could not decode as UTF-8, showing hex:")
            print(preview.hex())
    else:
        print("\nBoundary marker not found")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_eml_content(sys.argv[1])
    else:
        print("Usage: python find_eml.py <filename>")
        sys.exit(1)
