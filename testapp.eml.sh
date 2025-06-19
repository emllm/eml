#!/bin/bash
#
# Self-extracting EML script - faktury-maj.eml.sh
# Użycie: ./faktury-maj.eml.sh [extract|run|browse|info]
#
# Ten plik jest jednocześnie:
# 1. Wykonywalnym skryptem bash
# 2. Płynym plikiem EML z załącznikami
#

# Jeśli uruchomiono jako skrypt, obsłuż parametry
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    ACTION="${1:-browse}"
    SCRIPT_FILE="$0"
    TEMP_DIR="/tmp/webapp_$$"

    case "$ACTION" in
        "extract")
            echo "Wyodrębnianie plików z EML..."
            mkdir -p "$TEMP_DIR"

            # Znajdź początek EML (po komentarzach bash)
            EML_START=$(grep -n "^MIME-Version:" "$SCRIPT_FILE" | head -1 | cut -d: -f1)

            # Wyodrębnij część EML i przetwórz
            tail -n +$EML_START "$SCRIPT_FILE" > "$TEMP_DIR/content.eml"

            # Użyj Python do parsowania EML
            python3 -c "
import email
import os
import sys
import base64
import json

print('=== Debug: Starting EML parsing ===')
print('Opening file: ' + os.path.abspath('$TEMP_DIR/content.eml'))

with open('$TEMP_DIR/content.eml', 'rb') as f:
    msg = email.message_from_binary_file(f)
    print('Message type: ' + str(type(msg)))
    print('Message headers: ' + str(dict(msg.items())))

    extracted = []
    for part in msg.walk():
        print('\n=== Part Info ===')
        print('Content type: ' + part.get_content_type())
        print('Content disposition: ' + str(part.get('content-disposition')))
        print('Filename: ' + str(part.get_param('filename', header='content-disposition')))

        if part.get_content_maintype() == 'multipart':
            print('Skipping multipart')
            continue

        filename = part.get_param('filename', header='content-disposition')
        if not filename:
            content_type = part.get_content_type()
            print('No filename, using content type: ' + content_type)
            if content_type == 'text/html':
                filename = 'index.html'
            elif content_type == 'text/css':
                filename = 'style.css'
            elif content_type == 'application/javascript':
                filename = 'script.js'
            elif 'dockerfile' in content_type.lower():
                filename = 'Dockerfile'
            else:
                print('Unknown content type: ' + content_type)
                continue

        filepath = os.path.join('$TEMP_DIR', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            content = part.get_payload(decode=True)
            if content is None:
                content = part.get_payload().encode('utf-8')

            with open(filepath, 'wb') as f:
                f.write(content)

            extracted.append(filename)
            print('✓ ' + filename + ' (' + str(len(content)) + ' bytes)')

        except Exception as e:
            print('✗ Error extracting ' + filename + ': ' + str(e))
            import traceback
            print('Traceback:')
            print(traceback.format_exc())

print('\n=== Final Summary ===')
print('Extracted to: ' + os.path.abspath('$TEMP_DIR'))
print('Extracted files: ' + json.dumps(extracted, indent=2))
print('=== End of EML parsing ===')
"
            ;;

        "run")
            echo "Uruchamianie jako Docker container..."
            $0 extract

            if [ -f "$TEMP_DIR/Dockerfile" ]; then
                cd "$TEMP_DIR"
                docker build -t "webapp-$(basename $0 .eml.sh)" .
                echo "Starting container on http://localhost:8080"
                docker run --rm -p 8080:80 "webapp-$(basename $0 .eml.sh)"
            else
                echo "Błąd: Brak Dockerfile w EML"
                exit 1
            fi
            ;;

        "browse")
            echo "Otwieranie w przeglądarce..."
            $0 extract

            # Sprawdź najpierw w katalogu bieżącym
            if [ -f "index.html" ]; then
                echo "Znaleziono index.html w katalogu bieżącym"
                
                # Zamień Content-ID references na lokalne pliki
                python3 -c "
import re
import os

html_file = 'index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Zamień cid: references na lokalne pliki
content = re.sub(r'src=[\"\']cid:([^\"\'>]+)[\"\']', r'src=\"\1\"', content)
content = re.sub(r'href=[\"\']cid:([^\"\'>]+)[\"\']', r'href=\"\1\"', content)

# Dodać ścieżki do wszystkich plików
content = re.sub(r'<link rel=\"stylesheet\" href=\"([^\"]+)\"', r'<link rel=\"stylesheet\" href=\"./\1\"', content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

                # Otwórz w przeglądarce
                if command -v xdg-open > /dev/null; then
                    xdg-open "file://$PWD/index.html"
                elif command -v open > /dev/null; then
                    open "file://$PWD/index.html"
                else
                    echo "Otwórz w przeglądarce: file://$PWD/index.html"
            else
                echo "Błąd: Brak index.html w EML"
                exit 1
            fi
            ;;

        "info")
            echo "Informacje o aplikacji:"
            echo "Nazwa: $(grep -m 1 'X-App-Name:' "$SCRIPT_FILE" | cut -d: -f2-)"
            echo "Typ: $(grep -m 1 'X-App-Type:' "$SCRIPT_FILE" | cut -d: -f2-)"
            echo "Generator: $(grep -m 1 'X-Generator:' "$SCRIPT_FILE" | cut -d: -f2-)"
            ;;

        *)
            echo "Użycie: $0 [extract|run|browse|info]"
            echo ""
            echo "Komendy:"
            echo "  extract  - Wyodrębnij pliki do /tmp"
            echo "  run      - Uruchom jako Docker container"
            echo "  browse   - Otwórz w przeglądarce"
            echo "  info     - Pokaż informacje o pliku"
            exit 1
            ;;
    esac

    exit 0
fi

# ====================================================================
# PONIŻEJ ZACZYNA SIĘ CZĘŚĆ EML
# Ten kod nigdy nie będzie wykonany jako bash, ale będzie interpretowany
# jako prawidłowy plik EML przez email clients i parsery MIME
# ====================================================================

MIME-Version: 1.0
Subject: WebApp - Faktury Maj 2025
Content-Type: multipart/mixed; boundary="WEBAPP_BOUNDARY_12345"
X-App-Type: docker-webapp
X-App-Name: Faktury Maj 2025
X-Generator: EML-Script-Generator

--WEBAPP_BOUNDARY_12345
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="index.html"

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Faktur - Maj 2025</title>
    <link rel="stylesheet" href="cid:style_css">
</head>
<body>
    <header>
        <h1>📊 Dashboard Faktur - Maj 2025</h1>
        <nav>
            <button onclick="showAll()">Wszystkie</button>
            <button onclick="filterByStatus('paid')">Opłacone</button>
            <button onclick="filterByStatus('pending')">Oczekujące</button>
        </nav>
    </header>

    <main>
        <div class="stats">
            <div class="stat-card">
                <h3>Łączna wartość</h3>
                <span class="amount">15,750 PLN</span>
            </div>
            <div class="stat-card">
                <h3>Faktury opłacone</h3>
                <span class="count">8/12</span>
            </div>
        </div>

        <div class="invoice-grid" id="invoiceGrid">
            <div class="invoice-card" data-status="paid">
                <img src="cid:invoice1_thumb" alt="Faktura 001" class="thumbnail">
                <div class="invoice-info">
                    <h4>Faktura #2025/05/001</h4>
                    <p>Firma ABC Sp. z o.o.</p>
                    <span class="amount">2,500 PLN</span>
                    <span class="status paid">Opłacona</span>
                </div>
            </div>

            <div class="invoice-card" data-status="pending">
                <img src="cid:invoice2_thumb" alt="Faktura 002" class="thumbnail">
                <div class="invoice-info">
                    <h4>Faktura #2025/05/002</h4>
                    <p>XYZ Solutions</p>
                    <span class="amount">1,200 PLN</span>
                    <span class="status pending">Oczekuje</span>
                </div>
            </div>
        </div>
    </main>

    <script src="cid:script_js"></script>
</body>
</html>

--WEBAPP_BOUNDARY_12345
Content-Type: text/css
Content-ID: <style_css>
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="style.css"

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

h1 {
    color: #333;
    margin-bottom: 15px;
    font-size: 2.2em;
}

nav button {
    background: #667eea;
    color: white;
    border: none;
    padding: 10px 20px;
    margin-right: 10px;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
}

nav button:hover {
    background: #5a67d8;
    transform: translateY(-2px);
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.9);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
    color: #666;
    margin-bottom: 10px;
}

.amount {
    font-size: 1.8em;
    font-weight: bold;
    color: #667eea;
}

.count {
    font-size: 1.8em;
    font-weight: bold;
    color: #48bb78;
}

.invoice-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.invoice-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 20px;
    display: flex;
    gap: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.invoice-card:hover {
    transform: translateY(-5px);
}

.thumbnail {
    width: 80px;
    height: 100px;
    object-fit: cover;
    border-radius: 8px;
    border: 2px solid #eee;
}

.invoice-info h4 {
    color: #333;
    margin-bottom: 5px;
}

.invoice-info p {
    color: #666;
    margin-bottom: 10px;
}

.status {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
    margin-top: 10px;
    display: inline-block;
}

.status.paid {
    background: #c6f6d5;
    color: #22543d;
}

.status.pending {
    background: #fed7d7;
    color: #c53030;
}

--WEBAPP_BOUNDARY_12345
Content-Type: application/javascript
Content-ID: <script_js>
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="script.js"

function showAll() {
    const cards = document.querySelectorAll('.invoice-card');
    cards.forEach(card => card.style.display = 'flex');
}

function filterByStatus(status) {
    const cards = document.querySelectorAll('.invoice-card');
    cards.forEach(card => {
        if (card.dataset.status === status) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Animacja ładowania
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.invoice-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    console.log('Dashboard faktur załadowany - Maj 2025');
});

--WEBAPP_BOUNDARY_12345
Content-Type: image/jpeg
Content-ID: <invoice1_thumb>
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="invoice1_thumb.jpg"

/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAoAFADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBSEGMUFRBxMiYXEUMoGRoQgjscHwFSNC0eEzFmLwNHKC8SVDNaUmZEU4SWNY/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAVEQEBAAAAAAAAAAAAAAAAAAAAAf/aAAwDAQACEQMRAD8A/T6iiigKKKKAooooP//Z

--WEBAPP_BOUNDARY_12345
Content-Type: image/jpeg
Content-ID: <invoice2_thumb>
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="invoice2_thumb.jpg"

/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAoAFADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBSEGMUFRBxMiYXEUMoGRoQgjscHwFSNC0eEzFmLwNHKC8SVDNaUmZEU4SWRY/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAVEQEBAAAAAAAAAAAAAAAAAAAAAf/aAAwDAQACEQMRAD8A/T6iiigKKKKAooooP//Z

--WEBAPP_BOUNDARY_12345
Content-Type: text/plain
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="Dockerfile"

FROM nginx:alpine

# Kopiuj wszystkie pliki do nginx
COPY *.html /usr/share/nginx/html/
COPY *.css /usr/share/nginx/html/
COPY *.js /usr/share/nginx/html/
COPY *.jpg /usr/share/nginx/html/

# Konfiguracja nginx dla SPA
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Cache static assets \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

--WEBAPP_BOUNDARY_12345
Content-Type: application/json
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline; filename="metadata.json"

{
  "name": "Faktury Maj 2025",
  "version": "1.0.0",
  "description": "Dashboard faktur za maj 2025",
  "type": "webapp-eml",
  "created": "2025-06-19",
  "files": [
    "index.html",
    "style.css",
    "script.js",
    "invoice1_thumb.jpg",
    "invoice2_thumb.jpg",
    "Dockerfile"
  ],
  "stats": {
    "total_invoices": 12,
    "paid_invoices": 8,
    "total_amount": "15750 PLN"
  },
  "tags": ["faktury", "maj", "2025", "dashboard"]
}

--WEBAPP_BOUNDARY_12345--