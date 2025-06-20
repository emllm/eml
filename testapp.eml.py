#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
testapp.eml.py
Universal Self-extracting EML WebApp Script

Działa na: Windows, macOS, Linux
Wymagania: Python 3.6+ (standardowo dostępny)
Użycie: python testapp.eml.py [extract|run|browse|info]
        lub ./testapp.eml.py [extract|run|browse|info] (Linux/macOS)
        lub po prostu kliknij dwukrotnie na Windows

Ten plik jest jednocześnie:
1. Wykonywalnym skryptem Python
2. Prawidłowym plikiem EML z załącznikami
"""

import sys
import os
import tempfile
import webbrowser
import subprocess
import email
import mimetypes
import shutil
import platform
from pathlib import Path

# Uniwersalne funkcje pomocnicze
def get_platform():
    """Wykryj platformę systemową"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    else:
        return 'linux'


def show_notification(title, message):
    """Pokaż powiadomienie systemowe (cross-platform)"""
    try:
        system = get_platform()
        if system == 'windows':
            # Windows toast notification
            subprocess.run([
                'powershell', '-Command',
                f'Add-Type -AssemblyName System.Windows.Forms; '
                f'[System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
            ], check=False, capture_output=True)
        elif system == 'macos':
            # macOS notification
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}"'
            ], check=False, capture_output=True)
        else:
            # Linux notification (notify-send lub fallback)
            try:
                subprocess.run(['notify-send', title, message], check=False, capture_output=True)
            except:
                print(f"📱 {title}: {message}")
    except:
        print(f"📱 {title}: {message}")


def open_file_browser(path):
    """Otwórz plik w eksploratorze (cross-platform)"""
    try:
        system = get_platform()
        if system == 'windows':
            os.startfile(path)
        elif system == 'macos':
            subprocess.run(['open', path], check=False)
        else:
            subprocess.run(['xdg-open', path], check=False)
    except:
        print(f"📁 Otwórz: {path}")


def check_docker():
    """Sprawdź czy Docker jest dostępny"""
    try:
        import platform
        result = subprocess.run(['docker', '--version'],
                                capture_output=True, text=True, check=False)
        return result.returncode == 0
    except:
        return False


def extract_eml_content(script_path):
    """
    Wyodrębnij zawartość EML z pliku skryptu
    
    Args:
        script_path (str): Ścieżka do pliku skryptu .py lub .eml
        
    Returns:
        tuple: (ścieżka_do_pliku_eml, katalog_z_plikami)
    """
    temp_dir = tempfile.mkdtemp(prefix='webapp_')
    extracted_files = []

    try:
        print("\u2709 Wyszukiwanie zawartości EML w pliku...")
        
        # Read the input file as binary to avoid encoding issues
        with open(script_path, 'rb') as f:
            content = f.read()
        
        # Convert to string for searching
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = content.decode('latin-1')
        
        # Look for the EML content marker
        eml_marker = '# ===================================================================='
        eml_start = content_str.find(eml_marker)
        
        if eml_start == -1:
            raise ValueError("Nie znaleziono znacznika początku zawartości EML w pliku")
        
        # Find the start of the EML content (after the marker and any whitespace)
        eml_content_start = content_str.find('MIME-Version: 1.0', eml_start)
        if eml_content_start == -1:
            # Try with triple quotes
            eml_content_start = content_str.find('"""\nMIME-Version: 1.0', eml_start)
            if eml_content_start != -1:
                eml_content_start += 3  # Skip the triple quote and newline
        
        if eml_content_start == -1:
            raise ValueError("Nie udało się zlokalizować zawartości EML w pliku")
        
        # Extract the EML content
        eml_content = content_str[eml_content_start:]
        
        # Look for the end of the EML content (before the closing triple quotes or boundary)
        eml_end = eml_content.rfind('--UNIVERSAL_WEBAPP_BOUNDARY--')
        if eml_end == -1:
            eml_end = eml_content.rfind('"""')
        
        if eml_end != -1:
            eml_content = eml_content[:eml_end].strip()
        
        # Ensure we have a proper MIME-Version header at the start
        if not eml_content.startswith('MIME-Version'):
            mime_pos = eml_content.find('MIME-Version: 1.0')
            if mime_pos != -1:
                eml_content = eml_content[mime_pos:]
            else:
                # If we can't find MIME-Version, add a default header
                eml_content = 'MIME-Version: 1.0\n' + eml_content
        
        # Save the EML content to a temporary file
        eml_file = os.path.join(temp_dir, 'extracted.eml')
        with open(eml_file, 'w', encoding='utf-8') as f:
            f.write(eml_content)
        
        print(f"✅ Zapisano EML do: {eml_file}")
        
        # Also save a copy as content.eml for backward compatibility
        shutil.copy2(eml_file, os.path.join(temp_dir, 'content.eml'))
        
        # Now extract the files from the EML
        extracted_files = extract_from_eml(eml_file, temp_dir)
        
        # Verify extraction
        if not extracted_files:
            print("⚠ Nie wyodrębniono żadnych plików z EML!")
            # Try to read the EML file directly
            with open(eml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\nZawartość EML (pierwsze 500 znaków):\n{content[:500]}...")
        else:
            print(f"\n✅ Pomyślnie wyodrębniono {len(extracted_files)} plików:")
            for i, file_info in enumerate(extracted_files, 1):
                print(f"{i}. {file_info['name']} ({file_info['size']} bytes, {file_info['content_type']})")
        
        return eml_file, temp_dir
        
    except Exception as e:
        print(f" Błąd podczas wyodrębniania zawartości EML: {e}")
        raise

def extract_from_eml(eml_file, output_dir):
    """
    Extract files from an EML file
    
    Args:
        eml_file (str): Path to the EML file to extract from
        output_dir (str): Directory to extract files to
        
    Returns:
        list: List of dictionaries containing information about extracted files
    """
    extracted_files = []
    
    try:
        print(f"\n🔍 Analizowanie pliku EML: {eml_file}")
        
        # First try to parse the EML file
        with open(eml_file, 'r', encoding='utf-8') as f:
            msg = email.message_from_file(f)
            
        # If parsing fails, try reading as bytes
        if not msg:
            print("⚠ Nie udało się sparsować jako tekst, próbuję jako dane binarne...")
            with open(eml_file, 'rb') as f:
                msg = email.message_from_binary_file(f)
        
        if not msg:
            raise ValueError("Nie udało się sparsować pliku EML")
            
        print(f"\nPomyślnie sparsowano wiadomość EML (typ: {msg.get_content_type()})")
        
        # Print message structure for debugging
        print("\nStruktura wiadomości:")
        print(f"- Typ: {type(msg)}")
        print(f"- Czy multipart: {msg.is_multipart()}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Process all parts of the message
        for part in msg.walk():
            # Skip multipart container parts
            if part.get_content_maintype() == 'multipart':
                print(f"\nPomijam kontener multipart: {part.get_content_type()}")
                continue
                
            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition", "")
            
            # Get filename from headers or generate one
            filename = part.get_filename()
            if not filename and 'filename=' in content_disposition:
                # Extract filename from Content-Disposition if available
                filename = content_disposition.split('filename=')[1].strip('"\'')
            
            if not filename:
                # Generate a filename based on content type or part number
                ext = mimetypes.guess_extension(content_type) or '.bin'
                filename = f'part-{len(extracted_files)}{ext}'
            
            # Clean up filename
            filename = os.path.basename(filename).strip()
            if not filename:
                filename = f'part-{len(extracted_files)}.bin'
            
            # Save the file
            filepath = os.path.join(output_dir, filename)
            try:
                # Get the payload, handling both binary and text content
                payload = part.get_payload(decode=True)
                if payload is None:
                    payload = part.get_payload()
                    if isinstance(payload, str):
                        payload = payload.encode('utf-8')
                
                if payload:
                    # Ensure the directory exists
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Write the file
                    with open(filepath, 'wb') as f:
                        f.write(payload)
                    
                    # Get file size and add to extracted files list
                    file_size = os.path.getsize(filepath)
                    extracted_files.append({
                        'name': filename,
                        'path': filepath,
                        'size': file_size,
                        'content_type': content_type
                    })
                    
                    print(f"✅ {filename} ({file_size} bytes, {content_type})")
                
            except Exception as e:
                print(f"❌ Błąd podczas zapisywania pliku {filename}: {e}")
                continue
        
        if not extracted_files and not msg.is_multipart():
            # Handle non-multipart messages that didn't match our extraction logic
            try:
                filename = msg.get_filename() or 'content.bin'
                filepath = os.path.join(output_dir, filename)
                
                payload = msg.get_payload(decode=True) or msg.get_payload()
                if isinstance(payload, str):
                    payload = payload.encode('utf-8')
                
                with open(filepath, 'wb') as f:
                    f.write(payload)
                
                file_size = os.path.getsize(filepath)
                extracted_files.append({
                    'name': filename,
                    'path': filepath,
                    'size': file_size,
                    'content_type': msg.get_content_type()
                })
                print(f"✅ {filename} ({file_size} bytes, {msg.get_content_type()})")
            except Exception as e:
                print(f"❌ Błąd podczas zapisywania głównej zawartości: {e}")
        
        print(f"\n📁 Wyodrębniono {len(extracted_files)} plików do: {output_dir}")
        return extracted_files
        
    except Exception as e:
        print(f"❌ Błąd podczas przetwarzania pliku EML: {e}")
        raise


def action_extract(script_path):
    """Akcja: wyodrębnij pliki"""
    print("🔄 Wyodrębnianie plików z EML...")

    temp_dir, files = extract_eml_content(script_path)

    print(f"\n📁 Wyodrębniono {len(files)} plików do: {temp_dir}")

    # Pokaż powiadomienie
    show_notification("EML WebApp", f"Wyodrębniono {len(files)} plików")

    return temp_dir


def action_run(script_path):
    """Akcja: uruchom w Docker"""
    print("🐳 Uruchamianie jako kontener Docker...")

    if not check_docker():
        print("❌ Docker nie jest dostępny!")
        print("Zainstaluj Docker Desktop:")
        print("  Windows/macOS: https://www.docker.com/products/docker-desktop")
        print("  Linux: sudo apt install docker.io")
        return

    eml_file, temp_dir = extract_eml_content(script_path)
    
    # Look for Dockerfile in the extracted files
    dockerfile_path = None
    for root, _, files in os.walk(temp_dir):
        if 'Dockerfile' in files:
            dockerfile_path = os.path.join(root, 'Dockerfile')
            break
    
    if not dockerfile_path or not os.path.exists(dockerfile_path):
        print("❌ Brak Dockerfile w wyodrębnionych plikach")
        print(f"Przeszukiwano w: {temp_dir}")
        print(f"Zawartość katalogu: {os.listdir(temp_dir)}")
        return

    # Buduj obraz Docker
    script_name = Path(script_path).stem
    image_name = f"webapp-{script_name}"

    print(f"🔨 Budowanie obrazu Docker: {image_name}")

    try:
        # Przejdź do katalogu tymczasowego
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        # Buduj obraz
        build_result = subprocess.run([
            'docker', 'build', '-t', image_name, '.'
        ], capture_output=True, text=True)

        if build_result.returncode != 0:
            print(f"❌ Błąd budowania: {build_result.stderr}")
            return

        print("🚀 Uruchamianie kontenera na http://localhost:8080")
        show_notification("Docker WebApp", "Kontener uruchomiony na porcie 8080")

        # Otwórz przeglądarkę po chwili
        import threading
        def open_browser():
            import time
            time.sleep(3)
            webbrowser.open('http://localhost:8080')

        threading.Thread(target=open_browser, daemon=True).start()

        # Uruchom kontener
        subprocess.run([
            'docker', 'run', '--rm', '-p', '8080:80', image_name
        ])

    except KeyboardInterrupt:
        print("\n⏹️ Zatrzymano kontener")
    finally:
        os.chdir(original_dir)


def action_browse(script_path):
    """Akcja: otwórz w przeglądarce"""
    print("🌐 Otwieranie w przeglądarce...")

    temp_dir, files = extract_eml_content(script_path)

    # Znajdź index.html
    index_path = os.path.join(temp_dir, 'index.html')
    if not os.path.exists(index_path):
        print("❌ Brak index.html w EML")
        return

    # Zamień referencje CID na lokalne pliki
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Zastąp cid: referencje lokalnymi plikami
        html_content = re.sub(r'src="cid:([^"]+)"', r'src="\1"', html_content)
        html_content = re.sub(r'href="cid:([^"]+)"', r'href="\1"', html_content)

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Otwórz w przeglądarce
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
    help_text = """
🎯 EML WebApp - Uniwersalny samorozpakowujący się skrypt

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

📧 Ten plik jest również prawidłowym emailem EML!
"""
    print(help_text)


def main():
    """Główna funkcja"""
    script_path = os.path.abspath(__file__)

    # Obsługa argumentów
    action = 'browse'  # domyślna akcja
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()

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


# Uruchom tylko jeśli wywołano jako skrypt
if __name__ == '__main__':
    main()

# ====================================================================
# EML CONTENT STARTS HERE
# Ten kod nigdy nie będzie wykonany jako Python, ale będzie 
# interpretowany jako prawidłowy plik EML przez parsery MIME
# ====================================================================

"""
MIME-Version: 1.0
Subject: 🌍 Universal WebApp - Faktury Maj 2025
Content-Type: multipart/mixed; boundary="UNIVERSAL_WEBAPP_BOUNDARY"
X-App-Type: universal-webapp
X-App-Name: Faktury Maj 2025
X-Generator: Universal-EML-Script-Generator
X-Compatible-Platforms: Windows,macOS,Linux
X-Python-Version: 3.6+

--UNIVERSAL_WEBAPP_BOUNDARY
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="index.html"

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 Universal Dashboard - Faktury Maj 2025</title>
    <link rel="stylesheet" href="cid:style_css">
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
    </header>

    <main>
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-icon">💰</div>
                <div class="stat-content">
                    <h3>Łączna wartość</h3>
                    <span class="amount" id="totalAmount">15,750 PLN</span>
                </div>
            </div>

            <div class="stat-card paid">
                <div class="stat-icon">✅</div>
                <div class="stat-content">
                    <h3>Faktury opłacone</h3>
                    <span class="count" id="paidCount">8/12</span>
                </div>
            </div>

            <div class="stat-card pending">
                <div class="stat-icon">⏳</div>
                <div class="stat-content">
                    <h3>Oczekujące</h3>
                    <span class="count" id="pendingCount">4</span>
                </div>
            </div>

            <div class="stat-card progress">
                <div class="stat-icon">📊</div>
                <div class="stat-content">
                    <h3>Postęp</h3>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 67%"></div>
                    </div>
                    <span class="percentage">67%</span>
                </div>
            </div>
        </div>

        <div class="invoice-grid" id="invoiceGrid">
            <div class="invoice-card" data-status="paid" data-amount="2500">
                <div class="invoice-header">
                    <span class="invoice-number">#2025/05/001</span>
                    <span class="status paid">Opłacona</span>
                </div>
                <div class="invoice-content">
                    <img src="cid:invoice1_thumb" alt="Faktura 001" class="thumbnail">
                    <div class="invoice-details">
                        <h4>📄 Firma ABC Sp. z o.o.</h4>
                        <p class="description">Usługi IT - maj 2025</p>
                        <div class="amount-large">2,500 PLN</div>
                        <div class="invoice-meta">
                            <span>📅 2025-05-15</span>
                            <span>💳 Przelew</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="invoice-card" data-status="pending" data-amount="1200">
                <div class="invoice-header">
                    <span class="invoice-number">#2025/05/002</span>
                    <span class="status pending">Oczekuje</span>
                </div>
                <div class="invoice-content">
                    <img src="cid:invoice2_thumb" alt="Faktura 002" class="thumbnail">
                    <div class="invoice-details">
                        <h4>📄 XYZ Solutions</h4>
                        <p class="description">Konsultacje - maj 2025</p>
                        <div class="amount-large">1,200 PLN</div>
                        <div class="invoice-meta">
                            <span>📅 2025-05-20</span>
                            <span>⏳ 5 dni</span>
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