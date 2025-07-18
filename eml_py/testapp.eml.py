#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EML WebApp - Universal Web Application Packager

This script allows packaging web applications into a single EML file
that can be executed on any platform with Python 3.6+ or Docker.
"""

import email
import email.policy
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

def get_extract_dir() -> Path:
    """Get or create the extraction directory."""
    # Use eml_py/extracted_content instead of a temp directory
    script_dir = Path(__file__).parent.resolve()
    extract_dir = script_dir / 'extracted_content'
    
    # Create directory if it doesn't exist
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean the directory
    for item in extract_dir.glob('*'):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    
    print(f"📂 Using extraction directory: {extract_dir}")
    return extract_dir

# Add support for more MIME types
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('font/woff2', '.woff2')
mimetypes.add_type('font/woff', '.woff')
mimetypes.add_type('font/ttf', '.ttf')
mimetypes.add_type('font/eot', '.eot')

# Constants
DEFAULT_PORT = 8080
TEMP_PREFIX = 'webapp_'
EML_BOUNDARY = 'UNIVERSAL_WEBAPP_BOUNDARY'

def get_platform() -> str:
    """Detect the current platform.
    
    Returns:
        str: The detected platform ('windows', 'macos', or 'linux').
    """
    system = sys.platform.lower()
    if system == 'darwin':
        return 'macos'
    if system == 'win32':
        return 'windows'
    return 'linux'

def show_notification(title: str, message: str) -> None:
    """Display a system notification.
    
    Args:
        title: The title of the notification.
        message: The message content of the notification.
    """
    try:
        system = get_platform()
        if system == 'windows':
            subprocess.run(
                [
                    'powershell',
                    '-NoProfile',
                    '-ExecutionPolicy', 'Bypass',
                    '-Command',
                    f'[System.Windows.Forms.MessageBox]::Show(\"{message}\", \"{title}\")'
                ],
                check=False,
                capture_output=True
            )
        elif system == 'macos':
            subprocess.run(
                ['osascript', '-e', f'display notification "{message}" with title "{title}"'],
                check=False,
                capture_output=True
            )
        else:
            # Linux notification (notify-send or fallback)
            try:
                subprocess.run(
                    ['notify-send', title, message],
                    check=False,
                    capture_output=True
                )
            except (OSError, subprocess.SubprocessError) as e:
                print(f"{title}: {message}")
    except Exception as e:
        print(f"{title}: {message}")

def open_file_browser(path: str) -> None:
    """Open a file in the file browser"""
    try:
        system = get_platform()
        if system == 'windows':
            os.startfile(path)
        elif system == 'macos':
            subprocess.run(['open', path], check=False)
        else:
            subprocess.run(['xdg-open', path], check=False)
    except:
        print(f" Otwórz: {path}")

def check_docker() -> bool:
    """Check if Docker is available on the system.
    
    Returns:
        bool: True if Docker is available, False otherwise.
    """
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False

def extract_eml_content(script_path: Union[str, Path], output_dir: Optional[Union[str, Path]] = None) -> Tuple[Path, List[str]]:
    """Extract EML content from the script and save to files.
    
    Args:
        script_path: Path to the script containing EML content
        output_dir: Directory to extract files to. If None, uses the default extract directory.
        
    Returns:
        A tuple of (output_directory, list_of_extracted_files)
    """
    output_dir = Path(output_dir) if output_dir else get_extract_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        script_path = Path(script_path).resolve()
        print("🔍 Searching for EML content in script...")
        
        # Read the entire file as binary to avoid any encoding issues
        with open(script_path, 'rb') as f:
            script_content = f.read().decode('utf-8', errors='replace')
        
        # Find the EML content start marker
        start_marker = "# EML CONTENT STARTS HERE"
        start_idx = script_content.find(start_marker)
        if start_idx == -1:
            print("❌ EML start marker not found in script")
            return output_dir, []
        
        print(f"✅ Found EML start marker at position {start_idx}")
        
        # Find the start of the EML content after the marker
        # Look for the first line that starts with MIME-Version:
        lines = script_content.splitlines()
        eml_start_line = -1
        for i in range(len(lines)):
            if i * 100 < start_idx:  # Skip lines before our marker
                continue
                
            if lines[i].strip().startswith('MIME-Version:'):
                eml_start_line = i
                break
        
        if eml_start_line == -1:
            print("❌ Could not find start of EML content (MIME-Version header)")
            return output_dir, []
            
        print(f"✅ Found EML content start at line {eml_start_line}")
        
        # Find the end of the EML content
        eml_lines = []
        for i in range(eml_start_line, len(lines)):
            line = lines[i]
            eml_lines.append(line)
            
            # Check if we've reached the end of the EML content
            if line.strip() == '--UNIVERSAL_WEBAPP_BOUNDARY--':
                break
        
        # Join the lines to get the EML content
        eml_content = '\n'.join(eml_lines).strip()
        
        # Verify we have content
        if not eml_content:
            print("❌ No EML content found after start marker")
            return output_dir, []
        
        # Verify this looks like valid EML content
        if not eml_content.startswith('MIME-Version:'):
            print("❌ Invalid EML content: Missing MIME-Version header")
            print("First 100 chars of content:", eml_content[:100])
            return output_dir, []
            
        if 'Content-Type:' not in eml_content:
            print("❌ Invalid EML content: Missing Content-Type header")
            return output_dir, []
            
        # Ensure the EML content ends with the boundary
        boundary = '--UNIVERSAL_WEBAPP_BOUNDARY--'
        if not eml_content.strip().endswith(boundary):
            print("⚠️ Adding missing EML end boundary")
            eml_content = eml_content.rstrip() + "\n" + boundary + "\n"
        
        print(f"✅ Extracted {len(eml_content)} bytes of EML content")
        
        # Save the EML content
        eml_path = output_dir / 'original.eml'
        with open(eml_path, 'w', encoding='utf-8') as f:
            f.write(eml_content)
        
        # Extract files from EML
        extracted_files = extract_from_eml(eml_path, output_dir)
        print(f"\n✅ Extracted {len(extracted_files)} files to: {output_dir}")
        return output_dir, [f['filename'] for f in extracted_files if 'filename' in f]
        
    except Exception as e:
        print(f"❌ Error extracting EML content: {e}")
        import traceback
        traceback.print_exc()
        return output_dir, []

def update_html_references(html_path: str, cid_map: Dict[str, str]) -> None:
    """Update HTML file to use relative paths for resources (flat structure)
    
    Args:
        html_path: Path to the HTML file to update
        cid_map: Map of CID to filename
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update CSS and JS paths to use filenames directly (no subdirectories)
        content = re.sub(
            r'href=["\'](?:[^/]+/)*([^/"\']+\.css)["\']', 
            r'href="\1"', 
            content, 
            flags=re.IGNORECASE
        )
        content = re.sub(
            r'src=["\'](?:[^/]+/)*([^/"\']+\.js)["\']', 
            r'src="\1"', 
            content, 
            flags=re.IGNORECASE
        )
        content = re.sub(
            r'src=["\'](?:[^/]+/)*([^/"\']+\.(?:png|jpg|jpeg|gif|svg|ico))["\']', 
            r'src="\1"', 
            content, 
            flags=re.IGNORECASE
        )
        
        # Handle inline styles with url() references
        content = re.sub(
            r'url\(["\']?(?:[^/]+/)*([^/"\')]+\.(?:png|jpg|jpeg|gif|svg|ico))["\']?\)',
            r'url("\1")', 
            content, 
            flags=re.IGNORECASE
        )
        
        # Replace CID references with actual filenames
        for cid, filename in cid_map.items():
            # Handle both cid: and <cid> formats
            content = content.replace(f'cid:{cid}', filename)
            content = content.replace(f'<{cid}>', filename)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
                
    except Exception as e:
        print(f" Warning: Could not update HTML references in {html_path}: {e}")

def extract_from_eml(eml_file: str, output_dir: str) -> List[Dict]:
    """Extract files from an EML file with support for multipart/related and CID references.
    
    Args:
        eml_file: Path to the EML file
        output_dir: Directory to extract files to
        
    Returns:
        List of dictionaries with file information
    """
    extracted_files = []
    cid_map = {}
    
    try:
        print(f"\n🔍 Analyzing EML file: {eml_file}")
        
        # Read the raw content for debugging
        with open(eml_file, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
        
        print(f"📄 Raw content length: {len(raw_content)} bytes")
        print(f"📄 Content preview:\n{raw_content[:500]}...")
        
        # Try to parse as binary first
        with open(eml_file, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=email.policy.default)
        
        if not msg:
            print("❌ Failed to parse EML as binary, trying as text...")
            with open(eml_file, 'r', encoding='utf-8') as f:
                msg = email.message_from_file(f, policy=email.policy.default)
        
        if not msg:
            raise ValueError("❌ Failed to parse EML file using any method")
            
        print(f"✅ Successfully parsed EML message")
        print(f"📧 Content-Type: {msg.get_content_type()}")
        print(f"📧 Content-Disposition: {msg.get('Content-Disposition')}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Process all parts of the message
        for part in msg.walk():
            try:
                content_type = part.get_content_type()
                content_id = part.get("Content-ID", "").strip("<>")
                content_disposition = part.get("Content-Disposition", "")
                
                print(f"\n🔍 Processing part: {content_type}")
                print(f"   Content-ID: {content_id}")
                print(f"   Disposition: {content_disposition}")
                
                # Skip multipart container parts (we'll process their children)
                if part.is_multipart() and content_type != 'multipart/related':
                    print("   ↪️ Skipping multipart container")
                    continue
                
                # Get filename from Content-Disposition or Content-Type
                filename = part.get_filename()
                if not filename and content_id:
                    filename = f"{content_id}"
                    # Add appropriate extension based on content type
                    ext = mimetypes.guess_extension(part.get_content_type())
                    if ext and not filename.endswith(ext):
                        filename += ext
                
                # If still no filename, generate one
                if not filename:
                    ext = (mimetypes.guess_extension(part.get_content_type()) 
                           or '.bin')
                    filename = f"file_{len(extracted_files)}{ext}"
                
                # Clean filename and ensure it's safe
                filename = os.path.basename(filename)
                filename = re.sub(r'[^\w\-_. ]', '_', filename)
                
                # Ensure filename is unique
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(output_dir, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                # Map CID to filename for later reference
                if content_id and content_id not in cid_map:
                    cid_map[content_id] = filename
                    print(f"   📌 Mapped CID {content_id} to {filename}")
                
                # Save the file
                file_path = os.path.join(output_dir, filename)
                payload = part.get_payload(decode=True)
                if payload is None:
                    payload = part.get_payload()
                    if isinstance(payload, str):
                        payload = payload.encode('utf-8')
                
                if payload:
                    print(f"   💾 Saving {len(payload)} bytes to {filename}")
                    with open(file_path, 'wb') as f:
                        f.write(payload)
                    
                    # Add to extracted files list
                    file_info = {
                        'name': filename,
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'content_type': content_type,
                        'content_id': content_id
                    }
                    extracted_files.append(file_info)
                    print(f"Extracted: {filename} ({content_type})")
                
            except Exception as e:
                print(f"Error processing part: {e}")
                import traceback
                traceback.print_exc()
        
        # Update HTML files to fix resource references
        for file_info in extracted_files:
            if file_info['content_type'] == 'text/html':
                update_html_references(file_info['path'], cid_map)
        
        return extracted_files
        
    except Exception as e:
        print(f"Error processing EML: {e}")
        import traceback
        traceback.print_exc()
        return []

def action_extract(script_path: str, output_dir: str = None) -> str:
    """Extract EML content to the specified directory."""
    if output_dir is None:
        output_dir = get_extract_dir()
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        output_dir, extracted_files = extract_eml_content(script_path, output_dir)
        print(f"\n✅ Extracted {len(extracted_files)} files to: {output_dir}")
        print("\nExtracted files:")
        for file in sorted(extracted_files):
            print(f"- {file}")
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    # Extract files from EML
    extracted_files = extract_from_eml(eml_path, output_dir)
    print(f"\n✅ Extracted {len(extracted_files)} files to: {output_dir}")
    return output_dir


def action_browse(script_path: str) -> None:
    #Open the extracted content in the default browser.
    #
    #Args:
    #    script_path: Path to the script containing EML content
    #Extract and browse the EML content."""
    # Extract to a temporary directory
    temp_dir = action_extract(script_path)
    
    # Try to find index.html first
    index_path = os.path.join(temp_dir, 'index.html')
    
    # If index.html doesn't exist, try to find HTML content in the extracted files
    if not os.path.exists(index_path):
        print(" Looking for HTML content in EML...")
        
        # Look for HTML files in the extracted files
        html_files = [f for f in os.listdir(temp_dir) if f.endswith('.html')]
        if html_files:
            index_path = os.path.join(temp_dir, html_files[0])
            print(f" Found HTML file: {os.path.basename(index_path)}")
        else:
            # If no HTML files found, try to find HTML content in the EML
            eml_file = os.path.join(temp_dir, 'extracted.eml')
            if os.path.exists(eml_file):
                with open(eml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for HTML content in the EML
                html_start = content.find('<!DOCTYPE html>')
                if html_start == -1:
                    html_start = content.find('<html')
                    
                if html_start != -1:
                    # Create a temporary HTML file
                    index_path = os.path.join(temp_dir, 'index.html')
                    with open(index_path, 'w', encoding='utf-8') as f:
                        f.write(content[html_start:])
                    print(" Extracted HTML content from EML")
                else:
                    print(" No HTML content found in EML")
                    return
            else:
                print(" No EML file to process")
                return

    def update_html_links(html_file):
        """
        Update HTML file to use relative paths for resources (flat structure)
        
        Args:
            html_file (str): Path to the HTML file to update
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update CSS and JS paths to use filenames directly (no subdirectories)
            content = re.sub(r'href=["\'](?:[^/]+/)*([^/"\']+\.css)["\']', r'href="\1"', content, flags=re.IGNORECASE)
            content = re.sub(r'src=["\'](?:[^/]+/)*([^/"\']+\.js)["\']', r'src="\1"', content, flags=re.IGNORECASE)
            content = re.sub(r'src=["\'](?:[^/]+/)*([^/"\']+\.(?:png|jpg|jpeg|gif|svg|ico))["\']', r'src="\1"', content, flags=re.IGNORECASE)
            
            # Handle inline styles with url() references
            content = re.sub(r'url\(["\']?(?:[^/]+/)*([^/"\')]+\.(?:png|jpg|jpeg|gif|svg|ico))["\']?\)', 
                            r'url("\1")', content, flags=re.IGNORECASE)
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"⚠ Warning: Could not update HTML links in {html_file}: {e}")

    # Process the HTML file
    try:
        update_html_links(index_path)

        # Open in browser
        file_url = f"file://{index_path.replace(os.sep, '/')}"
        webbrowser.open(file_url)

        print(f"📱 Otwarto: {file_url}")
        show_notification("EML WebApp", "Aplikacja otwarta w przeglądarce")

    except Exception as e:
        print(f"❌ Błąd otwierania: {e}")


def action_info(script_path):
    """Akcja: pokaż informacje"""
    print("ℹ️  Informacje o EML WebApp:")
    print(f"📄 Plik: {script_path}")

    # Rozmiar pliku
    file_size = os.path.getsize(script_path)
    print(f"📊 Rozmiar: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # Informacje o systemie
    system_info = f"{platform.system()} {platform.release()}"
    print(f"💻 System: {system_info}")
    print(f"🐍 Python: {platform.python_version()}")

    # Sprawdź Docker
    docker_status = "✅ Dostępny" if check_docker() else "❌ Niedostępny"
    print(f"🐳 Docker: {docker_status}")

    try:
        # Wyodrębnij i policz pliki
        temp_dir, files = extract_eml_content(script_path)

        print(f"📦 Zawartość:")
        for file_info in files:
            print(f"   📄 {file_info['name']} ({file_info['size']} bytes)")

        # Sprawdź metadata
        metadata_path = os.path.join(temp_dir, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                print(f"🏷️  Nazwa: {metadata.get('name', 'N/A')}")
                print(f"📅 Wersja: {metadata.get('version', 'N/A')}")
                print(f"📝 Opis: {metadata.get('description', 'N/A')}")

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"❌ Błąd analizy: {e}")


def show_help():
    """Pokaż pomoc"""
    help_text = u"""
 EML WebApp - Uniwersalny samorozpakowujący się skrypt

💻 Użycie:
   python testapp.eml.py [komenda]
   ./testapp.eml.py [komenda]        (Linux/macOS)

📋 Komendy:
   extract  - Wyodrębnij pliki do katalogu tymczasowego
   run      - Uruchom jako kontener Docker (wymaga Docker)
   browse   - Otwórz w przeglądarce (domyślnie)
   info     - Pokaż informacje o pliku i systemie
   help     - Pokaż tę pomoc

🌍 Kompatybilność:
   ✅ Windows (Python 3.6+)
   ✅ macOS (Python 3.6+)
   ✅ Linux (Python 3.6+)

🔧 Wymagania:
   - Python 3.6+ (standardowo dostępny)
   - Docker (opcjonalnie, dla komendy 'run')

📧 Ten plik jest również prawidłowym emailem EML!"""
    print(help_text)


def get_eml_content():
    """Return the EML content as a properly formatted string.
    
    Returns:
        str: A complete EML message with HTML content and resources.
    """
    return """Return-Path: <>
MIME-Version: 1.0
Content-Type: multipart/related; boundary="UNIVERSAL_WEBAPP_BOUNDARY"
From: Universal WebApp <noreply@universal-webapp.example.com>
To: user@example.com
Subject: =?utf-8?q?=F0=9F=8C=8D_Universal_Dashboard_-_Faktury_Maj_2025?=
Date: Thu, 15 May 2025 14:30:00 +0200
Message-ID: <20250515123000.12345@universal-webapp.example.com>
X-Universal-WebApp: true
X-Generator: Universal-WebApp/1.0

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-ID: <index.html>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>&#x1F30D; Universal Dashboard - Faktury Maj 2025</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Universal Faktury Dashboard</h1>
            <p>Works on any platform with Python 3.6+</p>
        </header>
        <main class="main-content">
            <section class="stats">
                <div class="stat-card">
                    <h3>Total Invoices</h3>
                    <p class="stat-number">5</p>
                </div>
                <div class="stat-card">
                    <h3>Paid</h3>
                    <p class="stat-number">3</p>
                </div>
                <div class="stat-card">
                    <h3>Pending</h3>
                    <p class="stat-number">2</p>
                </div>
            </section>
            <section class="invoices">
                <h2>Recent Invoices</h2>
                <div class="invoice-list">
                    <!-- Invoice items will be dynamically added here -->
                </div>
            </section>
        </main>
        <footer>
            <p>&#x1F30D; Universal EML WebApp - Compatible with all platforms</p>
            <p>&#x1F40D; Powered by Python | &#x1F4E7; Valid EML format</p>
        </footer>
    </div>
    <script src="script.js"></script>
</body>
</html>

--UNIVERSAL_WEBAPP_BOUNDARY--
"""
                    <h3>Total Invoices</h3>
                    <p class=3D"stat-number">5</p>
                </div>
                <div class=3D"stat-card">
                    <h3>Paid</h3>
                    <p class=3D"stat-number">3</p>
                </div>
                <div class=3D"stat-card">
                    <h3>Pending</h3>
                    <p class=3D"stat-number">2</p>
                </div>
            </section>
            
            <section class=3D"invoices">
                <h2>Recent Invoices</h2>
                <div class=3D"invoice-list">
                    <div class=3D"invoice-item">
                        <div class=3D"invoice-preview">
                            <img src=3D"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAQABADASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdAB//2Q==" alt=3D"Invoice 1">
                        </div>
                        <div class=3D"invoice-details">
                            <h3>Faktura #001</h3>
                            <p>Status: <span class=3D"status-paid">Zapłacono</span></p>
                            <p>Kwota: 5,000 PLN</p>
                        </div>
                    </div>
                    <div class=3D"invoice-item">
                        <div class=3D"invoice-preview">
                            <img src=3D"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAQABADASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdAB//2Q==" alt=3D"Invoice 2">
                        </div>
                        <div class=3D"invoice-details">
                            <h3>Faktura #002</h3>
                            <p>Status: <span class=3D"status-pending">Oczekuje na płatność</span></p>
                            <p>Kwota: 2,500 PLN</p>
                        </div>
                    </div>
                </div>
            </section>
        </main>
        
        <footer class=3D"footer">
            <p>&#x1F30D; Universal EML WebApp - Compatible with all platforms</p>
            <p>&#x1F40D; Powered by Python | &#x1F4E7; Valid EML format</p>
        </footer>
    </div>
    <script src="script.js"></script>
</body>
</html>

--UNIVERSAL_WEBAPP_BOUNDARY--
"""

# Uruchom tylko jeśli wywołano jako skrypt
if __name__ == '__main__':
    main();
}

.invoice-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.invoice-item {
    border: 1px solid #ddd;
    border-radius: var(--border-radius);
    overflow: hidden;
    transition: transform 0.2s;
}

.invoice-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.invoice-preview img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.invoice-details {
    padding: 15px;
}

.invoice-details h3 {
    margin-bottom: 10px;
    color: var(--primary-color);
}

.status-paid {
    color: var(--success-color);
    font-weight: bold;
}

.status-pending {
    color: var(--danger-color);
    font-weight: bold;
}

.footer {
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-top: 1px solid #eee;
    margin-top: 30px;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1a1a1a;
        color: #f0f0f0;
    }
    
    .container {
        background: #2d2d2d;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    }
    
    .stat-card {
        background: #3a3a3a;
        color: #f0f0f0;
    }
    
    .invoice-item {
        border-color: #444;
    }
    
    .footer {
        background: #252525;
        border-top-color: #444;
    }
}

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: application/javascript; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="script.js"

class UniversalDashboard {
    constructor() {
        this.invoices = [];
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSampleData();
        this.render();
    }

    loadSampleData() {
        this.invoices = [
            { id: 1, number: 'INV-2023-001', amount: 5000, status: 'paid', date: '2023-06-01' },
            { id: 2, number: 'INV-2023-002', amount: 2500, status: 'pending', date: '2023-06-15' },
            { id: 3, number: 'INV-2023-003', amount: 1200, status: 'paid', date: '2023-05-20' },
            { id: 4, number: 'INV-2023-004', amount: 3200, status: 'paid', date: '2023-05-10' },
            { id: 5, number: 'INV-2023-005', amount: 2000, status: 'pending', date: '2023-04-28' }
        ];
    }

    render() {
        this.updateStats();
        this.renderInvoices();
    }

    updateStats() {
        const total = this.invoices.length;
        const paid = this.invoices.filter(inv => inv.status === 'paid').length;
        const pending = total - paid;
        
        document.querySelector('.stat-number:nth-child(1)').textContent = total;
        document.querySelector('.stat-number:nth-child(2)').textContent = paid;
        document.querySelector('.stat-number:nth-child(3)').textContent = pending;
    }

    renderInvoices() {
        const container = document.querySelector('.invoice-list');
        if (!container) return;
        
        let filteredInvoices = [...this.invoices];
        if (this.currentFilter === 'paid') {
            filteredInvoices = filteredInvoices.filter(inv => inv.status === 'paid');
        } else if (this.currentFilter === 'pending') {
            filteredInvoices = filteredInvoices.filter(inv => inv.status === 'pending');
        }
        
        container.innerHTML = filteredInvoices.map(invoice => `
            <div class="invoice-item">
                <div class="invoice-preview">
                    <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAQABADASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdAB//2Q==" alt="Invoice ${invoice.id}">
                </div>
                <div class="invoice-details">
                    <h3>${invoice.number}</h3>
                    <p>Status: <span class="status-${invoice.status}">
                        ${invoice.status === 'paid' ? 'Zapłacono' : 'Oczekuje na płatność'}
                    </span></p>
                    <p>Kwota: ${invoice.amount.toLocaleString()} PLN</p>
                </div>
            </div>
        `).join('');
    }

    showAll() {
        this.currentFilter = 'all';
        this.renderInvoices();
    }

    showPaid() {
        this.currentFilter = 'paid';
        this.renderInvoices();
    }

    showPending() {
        this.currentFilter = 'pending';
        this.renderInvoices();
    }

    setupEventListeners() {
        // Platform-specific keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            const isMac = this.getPlatform() === 'macos';
            const cmdKey = isMac ? e.metaKey : e.ctrlKey;
            
            // Cmd/Ctrl + F - Focus search
            if (cmdKey && e.key === 'f') {
                e.preventDefault();
                this.focusSearch();
            }
            
            // Cmd/Ctrl + S - Save
            if (cmdKey && e.key === 's') {
                e.preventDefault();
                this.saveChanges();
            }
        });
        
        // Handle window resize for responsive design
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // Add click handlers for filter buttons
        const filterButtons = document.querySelectorAll('[data-filter]');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.currentFilter = filter;
                this.renderInvoices();
                
                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }
    
    getPlatform() {
        const userAgent = navigator.userAgent.toLowerCase();
        if (userAgent.includes('win')) return 'windows';
        if (userAgent.includes('mac')) return 'macos';
        if (userAgent.includes('linux')) return 'linux';
        return 'unknown';
    }
    
    handleResize() {
        // Add responsive behavior here
        const container = document.querySelector('.container');
        if (window.innerWidth < 768) {
            container.classList.add('mobile-view');
        } else {
            container.classList.remove('mobile-view');
        }
    }
    
    focusSearch() {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    saveChanges() {
        this.showNotification('Zapisano zmiany', 'Twoje zmiany zostały zapisane pomyślnie.');
    }
    
    showNotification(title, message) {
        // Check if the browser supports notifications
        if (!('Notification' in window)) {
            this.showCustomNotification(title, message);
            return;
        }
        
        // Check if notification permissions have been granted
        if (Notification.permission === 'granted') {
            new Notification(title, { body: message });
        } 
        // Otherwise, ask for permission
        else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification(title, { body: message });
                } else {
                    this.showCustomNotification(title, message);
                }
            });
        } else {
            this.showCustomNotification(title, message);
        }
    }
    
    showCustomNotification(title, message) {
        // Create custom notification element
        const notification = document.createElement('div');
        notification.className = 'custom-notification';
        notification.innerHTML = `
            <h4>${title}</h4>
            <p>${message}</p>
            <button class="close-notification">×</button>
        `;
        
        // Style the notification
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        notification.style.padding = '15px';
        notification.style.backgroundColor = '#fff';
        notification.style.borderRadius = '4px';
        notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        notification.style.zIndex = '1000';
        notification.style.maxWidth = '300px';
        notification.style.transform = 'translateY(100px)';
        notification.style.opacity = '0';
        notification.style.transition = 'all 0.3s ease';
        
        // Add dark mode support
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            notification.style.backgroundColor = '#333';
            notification.style.color = '#fff';
        }
        
        // Add to document
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateY(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Auto-remove after 5 seconds
        const autoRemove = setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
        
        // Close button
        const closeButton = notification.querySelector('.close-notification');
        closeButton.addEventListener('click', () => {
            clearTimeout(autoRemove);
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        });
        
        // Pause auto-remove on hover
        notification.addEventListener('mouseenter', () => {
            clearTimeout(autoRemove);
        });
        
        // Resume auto-remove when mouse leaves
        notification.addEventListener('mouseleave', () => {
            setTimeout(() => {
                notification.style.transform = 'translateY(100px)';
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        });
    }
}

// Global functions for button callbacks
function showAll() {
    window.dashboard.showAll();
}

function showPaid() {
    window.dashboard.showPaid();
}

function showPending() {
    window.dashboard.showPending();
}

// Initialize the dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new UniversalDashboard();
    
    // Add platform class to body for platform-specific styling
    document.body.classList.add(`platform-${window.dashboard.getPlatform()}`);
    
    // Show welcome notification
    setTimeout(() => {
        window.dashboard.showNotification(
            'Witaj w Universal Faktury Dashboard!', 
            'Zacznij zarządzać swoimi fakturami na dowolnej platformie.'
        );
    }, 1000);
});

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="Dockerfile"

# Use a multi-stage build for smaller image size
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Second stage: runtime image
FROM python:3.9-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Expose the port the app runs on
EXPOSE 8080

# Labels for better maintainability
LABEL org.opencontainers.image.title="Universal WebApp"
LABEL org.opencontainers.image.description="A universal web application that works everywhere"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2025-06-19"

# Start nginx
CMD ["python", "-m", "http.server", "8080"]

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: application/json; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="metadata.json"

{
  "name": "Universal Faktury Dashboard",
  "version": "1.0.0",
  "description": "Cross-platform invoice dashboard - works on Windows, macOS, and Linux",
  "type": "universal-webapp-eml",
  "format": "eml-python-script",
  "created": "2025-06-19T10:00:00Z",
  "author": "Universal EML WebApp Generator",

  "compatibility": {
    "platforms": ["Windows", "macOS", "Linux", "Android", "iOS"],
    "browsers": ["Chrome", "Firefox", "Safari", "Edge"],
    "python_versions": ["3.6+", "3.7+", "3.8+", "3.9+", "3.10+", "3.11+"],
    "requirements": {
      "python3": "Built-in standard library only",
      "docker": "Optional - for 'run' command"
    }
  },

  "features": {
    "universal": true,
    "cross_platform": true,
    "self_extracting": true,
    "docker_ready": true,
    "responsive_design": true,
    "keyboard_shortcuts": true,
    "native_notifications": true,
    "touch_support": true,
    "dark_mode_support": true,
    "pwa_ready": false
  },

  "commands": {
    "extract": "Extract files to temporary directory",
    "run": "Run as Docker container on port 8080",
    "browse": "Open in system default browser",
    "info": "Show file and system information",
    "help": "Display usage instructions"
  },

  "files": [
    {
      "name": "index.html",
      "type": "text/html",
      "description": "Main dashboard interface",
      "features": ["responsive", "platform-detection", "animations"]
    },
    {
      "name": "style.css", 
      "type": "text/css",
      "description": "Universal stylesheet with platform optimizations",
      "features": ["cross-platform", "dark-mode", "responsive", "animations"]
    },
    {
      "name": "script.js",
      "type": "application/javascript", 
      "description": "Cross-platform JavaScript with platform detection",
      "features": ["platform-detection", "notifications", "keyboard-shortcuts", "touch-support"]
    },
    {
      "name": "Dockerfile",
      "type": "text/plain",
      "description": "Universal Docker configuration",
      "features": ["multi-platform", "health-checks", "optimized-nginx"]
    },
    {
      "name": "invoice1_thumb.jpg",
      "type": "image/jpeg",
      "description": "Sample invoice thumbnail"
    },
    {
      "name": "invoice2_thumb.jpg", 
      "type": "image/jpeg",
      "description": "Sample invoice thumbnail"
    }
  ],

  "usage_examples": {
    "windows": [
      "python testapp.eml.py",
      "python testapp.eml.py browse",
      "python testapp.eml.py run",
      "Double-click for GUI dialog"
    ],
    "macos": [
      "./testapp.eml.py",
      "python3 testapp.eml.py browse", 
      "python3 testapp.eml.py run"
    ],
    "linux": [
      "./testapp.eml.py",
      "python3 testapp.eml.py browse",
      "python3 testapp.eml.py run"
    ]
  },

  "business_data": {
    "total_invoices": 5,
    "paid_invoices": 3,
    "pending_invoices": 2,
    "total_amount": "13,900 PLN",
    "paid_amount": "9,900 PLN", 
    "pending_amount": "4,000 PLN",
    "completion_rate": "60%"
  },

  "technical_specs": {
    "file_size_mb": "< 2",
    "load_time_ms": "< 500",
    "supported_resolutions": ["320px+", "tablet", "desktop", "4K"],
    "mime_compliant": true,
    "email_client_compatible": true,
    "security": {
      "xss_protection": true,
      "csp_headers": true,
      "cors_enabled": true,
      "no_external_dependencies": true
    }
  },

  "development": {
    "build_system": "manual",
    "testing": "cross-platform",
    "deployment": "single-file",
    "maintenance": "zero-dependency"
  },

  "tags": [
    "universal", "cross-platform", "python", "eml", "webapp", 
    "self-extracting", "docker", "responsive", "faktury", 
    "dashboard", "maj-2025", "business"
  ]
}

--UNIVERSAL_WEBAPP_BOUNDARY--
"""
    print(help_text)


def main():
    """Główna funkcja"""
    import sys
    script_path = os.path.abspath(__file__)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'extract':
            output_dir = sys.argv[2] if len(sys.argv) > 2 else None
            action_extract(script_path, output_dir)
        elif command == 'browse':
            action_browse(script_path)
        elif command == 'run':
            action_run(script_path)
        elif command == 'info':
            action_info(script_path)
        elif command == 'help':
            show_help()
        else:
            print(f"Nieznana komenda: {command}")
            show_help()
    else:
        # Domyślna akcja - pokaż pomoc
        show_help()

if __name__ == "__main__":
    main()

    # Obsługa argumentów
    action = 'browse'  # domyślna akcja
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        # Handle extract with output directory
        if action == 'extract' and len(sys.argv) > 2:
            output_dir = sys.argv[2]
            action_extract(script_path, output_dir)
            return
        # Handle run with port
        elif action == 'run' and len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
                action_run(script_path, port)
                return
            except ValueError:
                print(f"Error: Invalid port number: {sys.argv[2]}")
                sys.exit(1)

    # GUI fallback dla Windows double-click
    if len(sys.argv) == 1 and get_platform() == 'windows':
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()  # Ukryj główne okno

            result = messagebox.askyesnocancel(
                "EML WebApp",
                "Wybierz akcję:\n\n"
                "TAK - Otwórz w przeglądarce\n"
                "NIE - Uruchom w Docker\n"
                "ANULUJ - Pokaż informacje"
            )

            if result is True:
                action = 'browse'
            elif result is False:
                action = 'run'
            else:
                action = 'info'

        except ImportError:
            pass  # Brak tkinter, użyj domyślnej akcji

    # Wykonaj akcję
    try:
        if action == 'extract':
            action_extract(script_path)
        elif action == 'run':
            action_run(script_path)
        elif action == 'browse':
            action_browse(script_path)
        elif action == 'info':
            action_info(script_path)
        elif action in ['help', '--help', '-h']:
            show_help()
        else:
            print(f"❌ Nieznana komenda: {action}")
            show_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ Anulowano przez użytkownika")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Błąd: {e}")
        sys.exit(1)


# ====================================================================
# EML CONTENT - This is a properly formatted EML file
# ====================================================================

def get_eml_content():
    """Return the EML content as a string."""
    return """MIME-Version: 1.0
Subject: =?utf-8?b?8J+MiSBVbml2ZXJzYWwgRGFzaGJvYXJkIC0gRmFrdHVyeSBNYWogMjAyNQ==?=
Content-Type: multipart/mixed; boundary=UNIVERSAL_WEBAPP_BOUNDARY
X-App-Type: universal-webapp
X-App-Name: Faktury Maj 2025
X-Generator: Universal-EML-Script-Generator
X-Compatible-Platforms: Windows,macOS,Linux
Python-Version: 3.6

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html>
<html lang="pl">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Universal Dashboard - Faktury</title>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
</head>
<body>
    <div class="platform-indicator" id="platformIndicator">
        <span id="platformIcon">🌍</span>
        <span id="platformName">Universal</span>
    </div>
    
    <div class="container">
        <h1>📊 Universal Faktury Dashboard</h1>
        <div class="stats">
            <div class="stat-card">
                <h3>Łącznie faktur</h3>
                <p class="stat-value" id="totalInvoices">5</p>
            </div>
            <div class="stat-card">
                <h3>Zapłacone</h3>
                <p class="stat-value" id="paidInvoices">3</p>
            </div>
            <div class="stat-card">
                <h3>Do zapłaty</h3>
                <p class="stat-value" id="pendingInvoices">2</p>
            </div>
        </div>
        
        <div class="actions">
            <button onclick="showAll()">Pokaż wszystkie</button>
            <button onclick="showPaid()">Tylko zapłacone</button>
            <button onclick="showPending()">Do zapłaty</button>
            <button onclick="addNew()">+ Nowa faktura</button>
        </div>
        
        <div id="invoiceList" class="invoice-list">
            <!-- Invoices will be dynamically inserted here -->
        </div>
    </div>
    
    <footer>
        <p>🌍 Universal EML WebApp - Compatible with all platforms</p>
        <p>🐍 Powered by Python | 📧 Valid EML format</p>
    </footer>
</body>
</html>

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/css; name="style.css"
Content-Disposition: attachment; filename="style.css"
Content-Transfer-Encoding: base64

LyogQmFzZSBzdHlsZXMgKi8KOmhvc3QgewogICAgLS1wcmltYXJ5OiAjNDI4NWY0OwogICAgLS1zZWNvbmRhcnk6ICMzNzc5YjU7CiAgICAtLXN1Y2Nlc3M6ICMyZTdlNGI7CiAgICAtLWluZm86ICMxN2EyYjg7CiAgICAtLXdhcm5pbmc6ICNmZjYwMDA7CiAgICAtLWRhbmdlcjogI2RjMzU0NTsKICAgIC0tbGlnaHQ6ICNmOGY5ZmE7CiAgICAtLWRhcms6ICMzNDNhNDA7CiAgICAtLWdyYXktMTAwOiAjZjhmOWZhOwogICAgLS1ncmF5LTIwMDogI2U5ZWNmMTsKICAgIC0tZ3JheS0zMDA6ICNkZWRlZTc7CiAgICAtLWdyYXktNDAwOiAjY2JkNWQzOwogICAgLS1ncmF5LTUwMDogIzllYTVhYjsKICAgIC0tZ3JheS02MDA6ICM2Yzc0ODA7CiAgICAtLWdyYXktNzAwOiAjNDk1MDU3OwogICAgLS1ncmF5LTgwMCAjM2QzYzRlOwogICAgLS1ncmF5LTkwMCAjMzQzYzQ3OwogICAgLS1mb250LXNhbnM6IC1hcHBsZS1zeXN0ZW0sIEJsaW5rTWFjU3lzdGVtRm9udCwgIlNlZ29lIFVJIiwgUm9ib3RvLCAiSGVsdmV0aWNhIE5ldWUiLCBBcmlhbCwgc2Fucy1zZXJpZiwgIkFwcGxlIENvbG9yIEVtb2ppIiwgIlNlZ29lIFVJIEVtb2ppIiwgIlNlZ29lIFVJIFN5bWJvbCI7Cn0KCmJvZHkgewogICAgZm9udC1mYW1pbHk6IHZhcigtLWZvbnQtc2Fucyk7CiAgICBsaW5lLWhlaWdodDogMS41OwogICAgY29sb3I6IHZhcigtLWRhcms7CiAgICBtYXJnaW46IDA7CiAgICBwYWRkaW5nOiAwOwogICAgYmFja2dyb3VuZC1jb2xvcjogI2Y4ZjlmYTsKfQoKLyogQ29udGFpbmVyICovCi5jb250YWluZXIgewogICAgbWF4LXdpZHRoOiAxMjAwcHg7CiAgICBtYXJnaW46IDAgYXV0bzsKICAgIHBhZGRpbmc6IDIwcHg7Cn0KCi8qIFBsYXRmb3JtIGluZGljYXRvciAqLwo="""

# Uruchom tylko jeśli wywołano jako skrypt
def get_eml_content():
    """Return the EML content as a string."""
    return """MIME-Version: 1.0
Subject: =?utf-8?b?8J+MiSBVbml2ZXJzYWwgRGFzaGJvYXJkIC0gRmFrdHVyeSBNYWogMjAyNQ==?=
Content-Type: multipart/mixed; boundary=UNIVERSAL_WEBAPP_BOUNDARY
X-App-Type: universal-webapp
X-App-Name: Faktury Maj 2025
X-Generator: Universal-EML-Script-Generator
X-Compatible-Platforms: Windows,macOS,Linux
Python-Version: 3.6

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 Universal Dashboard - Faktury Maj 2025</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="platform-indicator" id="platformIndicator">
        <span id="platformIcon">🌍</span>
        <span id="platformName">Universal</span>
    </div>

    <header>
        <h1>🌍 Universal Dashboard - Faktury Maj 2025</h1>
        <p class="subtitle">Działa na Windows, macOS i Linux</p>
        <nav>
            <button onclick="showAll()" class="btn-primary">Wszystkie</button>
            <button onclick="filterByStatus('paid')" class="btn-success">Opłacone</button>
            <button onclick="filterByStatus('pending')" class="btn-warning">Oczekujące</button>
            <button onclick="showStats()" class="btn-info">Statystyki</button>
        </nav>
    </header>"""

if __name__ == '__main__':
    main()
                        <h4>\U0001F4B0 XYZ Solutions</h4>
                        <p class="description">Konsultacje - maj 2025</p>
                        <div class="amount-large">1,200 PLN</div>
                        <div class="invoice-meta">
                            <span>\U0001F4C5 2025-05-20</span>
                            <span>\U0001F4CA Podsumowanie</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="invoice-card" data-status="paid" data-amount="3200">
                <div class="invoice-header">
                    <span class="invoice-number">#2025/05/003</span>
                    <span class="status paid">Opłacona</span>
                </div>
                <div class="invoice-content">
                    <img src="cid:invoice1_thumb" alt="Faktura 003" class="thumbnail">
                    <div class="invoice-details">
                        <h4>📄 Tech Innovators Ltd</h4>
                        <p class="description">Rozwój aplikacji</p>
                        <div class="amount-large">3,200 PLN</div>
                        <div class="invoice-meta">
                            <span>📅 2025-05-10</span>
                            <span>💳 BLIK</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer>
        <p>🌍 Universal EML WebApp - Compatible with all platforms</p>
        <p>🐍 Powered by Python | 📧 Valid EML format</p>
    </footer>

    <script src="cid:script_js"></script>
</body>
</html>

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/css
Content-ID: <style_css>
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="style.css"

/* Universal CSS - Cross-platform optimized styles */

:root {
    --primary-color: #007AFF;
    --success-color: #34C759;
    --warning-color: #FF9500;
    --danger-color: #FF3B30;
    --info-color: #5AC8FA;
    --gray-100: #F2F2F7;
    --gray-200: #E5E5EA;
    --gray-300: #D1D1D6;
    --gray-800: #1C1C1E;
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.15);
    --shadow-lg: 0 8px 25px rgba(0,0,0,0.2);
    --border-radius: 12px;
    --transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
                 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: var(--gray-800);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Platform indicator */
.platform-indicator {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: var(--shadow-sm);
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 8px;
}

header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    padding: 30px;
    margin: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-md);
    text-align: center;
}

h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 10px;
    background: linear-gradient(135deg, var(--primary-color), var(--info-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    color: var(--gray-600);
    font-size: 1.1rem;
    margin-bottom: 25px;
}

nav {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

/* Universal button styles */
button {
    padding: 12px 24px;
    border: none;
    border-radius: 25px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: var(--transition);
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-success {
    background: var(--success-color);
    color: white;
}

.btn-warning {
    background: var(--warning-color);
    color: white;
}

.btn-info {
    background: var(--info-color);
    color: white;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    filter: brightness(1.1);
}

button:active {
    transform: translateY(0);
}

/* Stats grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px;
    margin-bottom: 40px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 25px;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: 20px;
    transition: var(--transition);
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}

.stat-icon {
    font-size: 2.5rem;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--gray-100);
}

.stat-content h3 {
    font-size: 0.9rem;
    color: var(--gray-600);
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}

.amount, .count {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--primary-color);
}

.percentage {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--success-color);
}

/* Progress bar */
.progress-bar {
    width: 100%;
    height: 8px;
    background: var(--gray-200);
    border-radius: 4px;
    overflow: hidden;
    margin: 8px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--success-color), var(--info-color));
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* Invoice grid */
.invoice-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 25px;
    margin: 20px;
}

.invoice-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    transition: var(--transition);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.invoice-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}

.invoice-header {
    background: var(--gray-100);
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--gray-200);
}

.invoice-number {
    font-weight: 700;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: var(--gray-800);
}

.status {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status.paid {
    background: var(--success-color);
    color: white;
}

.status.pending {
    background: var(--warning-color);
    color: white;
}

.invoice-content {
    padding: 20px;
    display: flex;
    gap: 20px;
}

.thumbnail {
    width: 80px;
    height: 100px;
    object-fit: cover;
    border-radius: 8px;
    border: 2px solid var(--gray-200);
    flex-shrink: 0;
}

.invoice-details {
    flex: 1;
}

.invoice-details h4 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--gray-800);
}

.description {
    color: var(--gray-600);
    font-size: 0.9rem;
    margin-bottom: 12px;
}

.amount-large {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 10px;
}

.invoice-meta {
    display: flex;
    gap: 15px;
    font-size: 0.8rem;
    color: var(--gray-600);
}

.invoice-meta span {
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Footer */
footer {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 30px;
    margin: 40px 20px 20px 20px;
    border-radius: var(--border-radius);
    text-align: center;
    color: white;
}

footer p {
    margin-bottom: 5px;
}

/* Responsive design */
@media (max-width: 768px) {
    h1 {
        font-size: 2rem;
    }

    nav {
        flex-direction: column;
        align-items: center;
    }

    button {
        width: 100%;
        max-width: 200px;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .invoice-grid {
        grid-template-columns: 1fr;
    }

    .invoice-content {
        flex-direction: column;
        text-align: center;
    }

    .thumbnail {
        align-self: center;
    }
}

/* Platform-specific optimizations */
@media (min-width: 1200px) {
    .stats-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}

/* Animation keyframes */
@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.animate-slide-in {
    animation: slideInUp 0.5s ease-out;
}

.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --gray-100: #1C1C1E;
        --gray-200: #2C2C2E;
        --gray-300: #3A3A3C;
        --gray-800: #F2F2F7;
    }

    body {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
}

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: application/javascript
Content-ID: <script_js>
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="script.js"

// Universal JavaScript - Cross-platform compatible
// Supports: Windows, macOS, Linux browsers

class UniversalDashboard {
    constructor() {
        this.invoices = [];
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.detectPlatform();
        this.loadInvoiceData();
        this.setupEventListeners();
        this.animateOnLoad();
        this.showWelcomeMessage();
    }

    detectPlatform() {
        const platform = this.getPlatform();
        const indicator = document.getElementById('platformIndicator');
        const platformName = document.getElementById('platformName');
        const platformIcon = document.getElementById('platformIcon');

        const platforms = {
            'windows': { icon: '🪟', name: 'Windows' },
            'macos': { icon: '🍎', name: 'macOS' },
            'linux': { icon: '🐧', name: 'Linux' },
            'android': { icon: '🤖', name: 'Android' },
            'ios': { icon: '📱', name: 'iOS' },
            'unknown': { icon: '🌍', name: 'Universal' }
        };

        const detected = platforms[platform] || platforms.unknown;
        platformIcon.textContent = detected.icon;
        platformName.textContent = detected.name;

        console.log(`🌍 Platform detected: ${detected.name}`);
    }

    getPlatform() {
        const userAgent = navigator.userAgent.toLowerCase();
        const platform = navigator.platform.toLowerCase();

        if (userAgent.includes('win') || platform.includes('win')) return 'windows';
        if (userAgent.includes('mac') || platform.includes('mac')) return 'macos';
        if (userAgent.includes('linux') || platform.includes('linux')) return 'linux';
        if (userAgent.includes('android')) return 'android';
        if (userAgent.includes('iphone') || userAgent.includes('ipad')) return 'ios';

        return 'unknown';
    }

    loadInvoiceData() {
        // Symulacja danych faktur
        this.invoices = [
            {
                id: '2025/05/001',
                company: 'Firma ABC Sp. z o.o.',
                description: 'Usługi IT - maj 2025',
                amount: 2500,
                status: 'paid',
                date: '2025-05-15',
                payment: 'Przelew'
            },
            {
                id: '2025/05/002', 
                company: 'XYZ Solutions',
                description: 'Konsultacje - maj 2025',
                amount: 1200,
                status: 'pending',
                date: '2025-05-20',
                payment: '5 dni'
            },
            {
                id: '2025/05/003',
                company: 'Tech Innovators Ltd',
                description: 'Rozwój aplikacji',
                amount: 3200,
                status: 'paid',
                date: '2025-05-10',
                payment: 'BLIK'
            },
            {
                id: '2025/05/004',
                company: 'Digital Marketing Pro',
                description: 'Kampania reklamowa',
                amount: 1800,
                status: 'pending',
                date: '2025-05-25',
                payment: '2 dni'
            },
            {
                id: '2025/05/005',
                company: 'Cloud Services Inc',
                description: 'Infrastruktura chmurowa',
                amount: 4200,
                status: 'paid',
                date: '2025-05-08',
                payment: 'Przelew'
            }
        ];

        this.updateStatistics();
    }

    updateStatistics() {
        const totalAmount = this.invoices.reduce((sum, inv) => sum + inv.amount, 0);
        const paidInvoices = this.invoices.filter(inv => inv.status === 'paid');
        const pendingInvoices = this.invoices.filter(inv => inv.status === 'pending');

        document.getElementById('totalAmount').textContent = 
            `${totalAmount.toLocaleString()} PLN`;
        document.getElementById('paidCount').textContent = 
            `${paidInvoices.length}/${this.invoices.length}`;
        document.getElementById('pendingCount').textContent = 
            pendingInvoices.length.toString();

        // Update progress bar
        const progressPercentage = Math.round((paidInvoices.length / this.invoices.length) * 100);
        const progressFill = document.querySelector('.progress-fill');
        const percentageSpan = document.querySelector('.percentage');

        if (progressFill && percentageSpan) {
            progressFill.style.width = `${progressPercentage}%`;
            percentageSpan.textContent = `${progressPercentage}%`;
        }
    }

    setupEventListeners() {
        // Platform-specific keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            const isMac = this.getPlatform() === 'macos';
            const cmdKey = isMac ? e.metaKey : e.ctrlKey;

            if (cmdKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.showAll();
                        break;
                    case '2':
                        e.preventDefault();
                        this.filterByStatus('paid');
                        break;
                    case '3':
                        e.preventDefault();
                        this.filterByStatus('pending');
                        break;
                    case 'i':
                        e.preventDefault();
                        this.showStats();
                        break;
                }
            }
        });

        // Touch/click handlers for mobile
        if ('ontouchstart' in window) {
            this.setupTouchHandlers();
        }
    }

    setupTouchHandlers() {
        const cards = document.querySelectorAll('.invoice-card');
        cards.forEach(card => {
            card.addEventListener('touchstart', (e) => {
                card.style.transform = 'scale(0.98)';
            });

            card.addEventListener('touchend', (e) => {
                card.style.transform = '';
            });
        });
    }

    showAll() {
        const cards = document.querySelectorAll('.invoice-card');
        cards.forEach(card => {
            card.style.display = 'block';
            card.classList.add('animate-fade-in');
        });
        this.currentFilter = 'all';
        this.updateFilterButtons();
    }

    filterByStatus(status) {
        const cards = document.querySelectorAll('.invoice-card');
        cards.forEach(card => {
            if (card.dataset.status === status) {
                card.style.display = 'block';
                card.classList.add('animate-slide-in');
            } else {
                card.style.display = 'none';
            }
        });
        this.currentFilter = status;
        this.updateFilterButtons();
    }

    updateFilterButtons() {
        const buttons = document.querySelectorAll('nav button');
        buttons.forEach(btn => btn.classList.remove('active'));

        // Add visual feedback for active filter
        const activeButton = document.querySelector(`button[onclick*="${this.currentFilter}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }

    showStats() {
        const stats = this.calculateDetailedStats();
        this.showNotification('Statystyki', JSON.stringify(stats, null, 2));
    }

    calculateDetailedStats() {
        const paid = this.invoices.filter(inv => inv.status === 'paid');
        const pending = this.invoices.filter(inv => inv.status === 'pending');

        return {
            total_invoices: this.invoices.length,
            paid_invoices: paid.length,
            pending_invoices: pending.length,
            total_amount: this.invoices.reduce((sum, inv) => sum + inv.amount, 0),
            paid_amount: paid.reduce((sum, inv) => sum + inv.amount, 0),
            pending_amount: pending.reduce((sum, inv) => sum + inv.amount, 0),
            average_invoice: Math.round(this.invoices.reduce((sum, inv) => sum + inv.amount, 0) / this.invoices.length)
        };
    }

    showNotification(title, message) {
        // Universal notification system
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, { body: message });
        } else if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification(title, { body: message });
                }
            });
        } else {
            // Fallback: console log or custom modal
            console.log(`📱 ${title}: ${message}`);
            this.showCustomNotification(title, message);
        }
    }

    showCustomNotification(title, message) {
        // Create custom notification element
        const notification = document.createElement('div');
        notification.className = 'custom-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <h4>${title}</h4>
                <p>${message}</p>
                <button onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            padding: 20px;
            max-width: 300px;
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    animateOnLoad() {
        // Staggered animation for cards
        const cards = document.querySelectorAll('.invoice-card');
        const statCards = document.querySelectorAll('.stat-card');

        // Animate stats first
        statCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';

            setTimeout(() => {
                card.style.transition = 'all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Then animate invoice cards
        setTimeout(() => {
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';

                setTimeout(() => {
                    card.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 120);
            });
        }, 400);
    }

    showWelcomeMessage() {
        setTimeout(() => {
            const platform = this.getPlatform();
            const platformNames = {
                'windows': 'Windows',
                'macos': 'macOS', 
                'linux': 'Linux',
                'android': 'Android',
                'ios': 'iOS',
                'unknown': 'Universal Platform'
            };

            const message = `Witaj w Universal Dashboard!\nPlatforma: ${platformNames[platform] || 'Universal'}\nWszystko działa poprawnie! 🎉`;

            console.log('🎯 Universal EML WebApp loaded successfully');
            console.log(`📱 Platform: ${platformNames[platform] || 'Universal'}`);
            console.log('🌍 Cross-platform compatibility: ✅');

            // Show welcome notification
            this.showNotification('Universal Dashboard', 'Aplikacja załadowana pomyślnie!');

        }, 1500);
    }
}

// Global functions for button callbacks
function showAll() {
    window.dashboard.showAll();
}

function filterByStatus(status) {
    window.dashboard.filterByStatus(status);
}

function showStats() {
    window.dashboard.showStats();
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new UniversalDashboard();

    console.log('🌍 Universal EML WebApp - Ready for all platforms!');
    console.log('🎯 Commands available: showAll(), filterByStatus(), showStats()');
    console.log('⌨️  Keyboard shortcuts: Ctrl/Cmd + 1,2,3,i');
});

// Service Worker registration for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Only register if we're not in file:// protocol
        if (location.protocol !== 'file:') {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => console.log('SW registered'))
                .catch(error => console.log('SW registration failed'));
        }
    });
}

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/plain
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="Dockerfile"

# Universal Dockerfile - optimized for all platforms
FROM nginx:alpine

LABEL maintainer="Universal EML WebApp"
LABEL description="Cross-platform Dashboard - Faktury Maj 2025"
LABEL platforms="linux/amd64,linux/arm64,windows,macos"

# Create app directory
WORKDIR /usr/share/nginx/html

# Copy all web assets
COPY *.html ./
COPY *.css ./
COPY *.js ./
COPY *.jpg ./
COPY *.json ./

# Create optimized nginx configuration
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Universal CORS and security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    add_header Referrer-Policy "strict-origin-when-cross-origin" always; \
    \
    # Enable CORS for local development \
    add_header Access-Control-Allow-Origin "*" always; \
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always; \
    add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept" always; \
    \
    # Main location block \
    location / { \
        try_files $uri $uri/ /index.html; \
        \
        # Cache control for HTML \
        location ~* \\html$ { \
            expires 1h; \
            add_header Cache-Control "public, must-revalidate"; \
        } \
    } \
    \
    # Static assets with long cache        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
        access_log off; \
    } \
    \
    # JSON files \
    location ~* \.json$ { \
        expires 1h; \
        add_header Content-Type "application/json"; \
    } \
    \
    # Gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types \
        text/plain \
        text/css \
        text/xml \
        text/javascript \
        application/javascript \
        application/json \
        application/xml+rss; \
    \
    # Security: disable server tokens \
    server_tokens off; \
    \
    # Handle favicon requests \
    location = /favicon.ico { \
        access_log off; \
        log_not_found off; \
    } \
    \
    # Health check endpoint \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

# Create health check script
RUN echo '#!/bin/sh\ncurl -f http://localhost/health || exit 1' > /health-check.sh && \
    chmod +x /health-check.sh

# Expose port
EXPOSE 80

# Health check for all platforms
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /health-check.sh

# Labels for better Docker management
LABEL org.opencontainers.image.title="Universal EML WebApp"
LABEL org.opencontainers.image.description="Cross-platform invoice dashboard"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2025-06-19"

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: application/json
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="metadata.json"

{
  "name": "Universal Faktury Dashboard",
  "version": "1.0.0",
  "description": "Cross-platform invoice dashboard - works on Windows, macOS, and Linux",
  "type": "universal-webapp-eml",
  "format": "eml-python-script",
  "created": "2025-06-19T10:00:00Z",
  "author": "Universal EML WebApp Generator",

  "compatibility": {
    "platforms": ["Windows", "macOS", "Linux", "Android", "iOS"],
    "browsers": ["Chrome", "Firefox", "Safari", "Edge"],
    "python_versions": ["3.6+", "3.7+", "3.8+", "3.9+", "3.10+", "3.11+"],
    "requirements": {
      "python3": "Built-in standard library only",
      "docker": "Optional - for 'run' command"
    }
  },

  "features": {
    "universal": true,
    "cross_platform": true,
    "self_extracting": true,
    "docker_ready": true,
    "responsive_design": true,
    "keyboard_shortcuts": true,
    "native_notifications": true,
    "touch_support": true,
    "dark_mode_support": true,
    "pwa_ready": false
  },

  "commands": {
    "extract": "Extract files to temporary directory",
    "run": "Run as Docker container on port 8080",
    "browse": "Open in system default browser",
    "info": "Show file and system information",
    "help": "Display usage instructions"
  },

  "files": [
    {
      "name": "index.html",
      "type": "text/html",
      "description": "Main dashboard interface",
      "features": ["responsive", "platform-detection", "animations"]
    },
    {
      "name": "style.css", 
      "type": "text/css",
      "description": "Universal stylesheet with platform optimizations",
      "features": ["cross-platform", "dark-mode", "responsive", "animations"]
    },
    {
      "name": "script.js",
      "type": "application/javascript", 
      "description": "Cross-platform JavaScript with platform detection",
      "features": ["platform-detection", "notifications", "keyboard-shortcuts", "touch-support"]
    },
    {
      "name": "Dockerfile",
      "type": "text/plain",
      "description": "Universal Docker configuration",
      "features": ["multi-platform", "health-checks", "optimized-nginx"]
    },
    {
      "name": "invoice1_thumb.jpg",
      "type": "image/jpeg",
      "description": "Sample invoice thumbnail"
    },
    {
      "name": "invoice2_thumb.jpg", 
      "type": "image/jpeg",
      "description": "Sample invoice thumbnail"
    }
  ],

  "usage_examples": {
    "windows": [
      "python testapp.eml.py",
      "python testapp.eml.py browse",
      "python testapp.eml.py run",
      "Double-click for GUI dialog"
    ],
    "macos": [
      "./testapp.eml.py",
      "python3 testapp.eml.py browse", 
      "python3 testapp.eml.py run"
    ],
    "linux": [
      "./testapp.eml.py",
      "python3 testapp.eml.py browse",
      "python3 testapp.eml.py run"
    ]
  },

  "business_data": {
    "total_invoices": 5,
    "paid_invoices": 3,
    "pending_invoices": 2,
    "total_amount": "13,900 PLN",
    "paid_amount": "9,900 PLN", 
    "pending_amount": "4,000 PLN",
    "completion_rate": "60%"
  },

  "technical_specs": {
    "file_size_mb": "< 2",
    "load_time_ms": "< 500",
    "supported_resolutions": ["320px+", "tablet", "desktop", "4K"],
    "mime_compliant": true,
    "email_client_compatible": true,
    "security": {
      "xss_protection": true,
      "csp_headers": true,
      "cors_enabled": true,
      "no_external_dependencies": true
    }
  },

  "development": {
    "build_system": "manual",
    "testing": "cross-platform",
    "deployment": "single-file",
    "maintenance": "zero-dependency"
  },

  "tags": [
    "universal", "cross-platform", "python", "eml", "webapp", 
    "self-extracting", "docker", "responsive", "faktury", 
    "dashboard", "maj-2025", "business"
  ]
}

--UNIVERSAL_WEBAPP_BOUNDARY--
"""