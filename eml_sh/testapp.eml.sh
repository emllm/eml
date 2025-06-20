Content-Type: multipart/alternative; boundary="WEBAPP_BOUNDARY_12345"
From: sender@example.com
To: recipient@example.com
Subject: Test Message
Date: Wed, 21 Jun 2025 10:00:00 +0000
#!/bin/bash
#
# Self-extracting EML script - testapp.eml.sh
# Użycie: ./testapp.eml.sh [extract|run|browse|info]
#
# Ten plik jest jednocześnie:
# 1. Wykonywalnym skryptem bash
# 2. Płynym plikiem EML z załącznikami
#

# Skip email headers if present
if [ "$1" = "Content-Type:" ] || [ "$1" = "From:" ] || [ "$1" = "To:" ] || [ "$1" = "Subject:" ] || [ "$1" = "Date:" ]; then
    # This is being called with email headers, skip execution
    exit 0
fi

# Znajdź i wykonaj tylko część bashową
if [ "$1" = "extract" ] || [ "$1" = "run" ] || [ "$1" = "browse" ] || [ "$1" = "info" ]; then
    # Przetwarzanie argumentów
    case "$1" in
        extract)
            echo "Wyodrębnianie zawartości..."
            EXTRACTED_DIR="$(pwd)/extracted_content"
            mkdir -p "$EXTRACTED_DIR"
            
            # Wyodrębnij HTML
            sed -n '/^<\!DOCTYPE html>/,/^<\/html>$/p' "$0" > "$EXTRACTED_DIR/index.html"
            
            # Wyodrębnij CSS
            if grep -q 'Content-Type: text/css' "$0"; then
                echo "Znaleziono plik CSS, wyodrębniam..."
                sed -n '/Content-Type: text\/css/,/--WEBAPP_BOUNDARY_/p' "$0" | \
                    sed '1d;$d' | base64 -d > "$EXTRACTED_DIR/style.css" 2>/dev/null || \
                    sed -n '/Content-Type: text\/css/,/--WEBAPP_BOUNDARY_/p' "$0" | \
                    sed '1d;$d' > "$EXTRACTED_DIR/style.css"
            fi
            
            # Extract JavaScript
            if grep -q 'Content-Type: application/javascript' "$0"; then
                echo "Znaleziono plik JavaScript, wyodrębniam..."
                
                # Directly write the JavaScript content we want to extract
                cat > "$EXTRACTED_DIR/app.js" << 'JS_EOF'
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
JS_EOF

                # Ensure proper permissions
                chmod 644 "$EXTRACTED_DIR/app.js"
            fi
            
            # Wyodrębnij favicon
            if grep -q 'Content-Type: image/svg+xml.*favicon' "$0"; then
                echo "Znaleziono favicon, wyodrębniam..."
                sed -n '/Content-Type: image\/svg\+xml.*favicon/,/--WEBAPP_BOUNDARY_/p' "$0" | \
                    grep -v '^Content-' | \
                    base64 -d > "$EXTRACTED_DIR/favicon.svg" 2>/dev/null || \
                    sed -n '/Content-Type: image\/svg\+xml.*favicon/,/--WEBAPP_BOUNDARY_/p' "$0" | \
                    grep -v '^Content-' > "$EXTRACTED_DIR/favicon.svg"
            fi
            
            # Create the HTML with CID references
            echo "Tworzenie wersji HTML z referencjami CID..."
            cat "$EXTRACTED_DIR/index.html" | \
                sed 's|href="css/style.css"|href="cid:style_css"|g' | \
                sed 's|src="js/app.js"|src="cid:script_js"|g' | \
                sed 's|href="images/favicon.svg"|href="cid:favicon_svg"|g' > "$EXTRACTED_DIR/cid_index.html"
            
            # Create a temporary file for the EML content
            TMP_EML="$EXTRACTED_DIR/original.eml"
            
            # Write headers to the temporary file
            cat > "$TMP_EML" <<- EOM
MIME-Version: 1.0
From: system@example.com
To: recipient@example.com
Subject: WebApp - Faktury Maj 2025
X-App-Type: docker-webapp
X-App-Name: Faktury Maj 2025
X-Generator: EML-Script-Generator
Content-Type: multipart/mixed; boundary="WEBAPP_BOUNDARY_12345"

--WEBAPP_BOUNDARY_12345
Content-Type: multipart/related; boundary="RELATED_BOUNDARY_12345"

--RELATED_BOUNDARY_12345
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-ID: <main_html>

EOM

            # Add HTML content
            cat "$EXTRACTED_DIR/cid_index.html" >> "$TMP_EML"
            
            # Add CSS part if exists
            if [ -f "$EXTRACTED_DIR/style.css" ]; then
                cat >> "$TMP_EML" <<- EOM

--RELATED_BOUNDARY_12345
Content-Type: text/css; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-ID: <style_css>
Content-Disposition: inline; filename="style.css"

EOM
                # Add CSS content
                cat "$EXTRACTED_DIR/style.css" >> "$TMP_EML"
            fi
            
            # Add JavaScript part if exists
            if [ -f "$EXTRACTED_DIR/app.js" ]; then
                cat >> "$TMP_EML" <<- EOM

--RELATED_BOUNDARY_12345
Content-Type: application/javascript; charset=utf-8
Content-Transfer-Encoding: quoted-printable
Content-ID: <script_js>
Content-Disposition: inline; filename="app.js"

EOM
                # Add JavaScript content
                cat "$EXTRACTED_DIR/app.js" >> "$TMP_EML"
            fi
            
            # Add favicon if exists
            if [ -f "$EXTRACTED_DIR/favicon.svg" ]; then
                cat >> "$TMP_EML" <<- EOM

--RELATED_BOUNDARY_12345
Content-Type: image/svg+xml; charset=utf-8
Content-Transfer-Encoding: base64
Content-ID: <favicon_svg>
Content-Disposition: inline; filename="favicon.svg"

EOM
                base64 < "$EXTRACTED_DIR/favicon.svg" >> "$TMP_EML"
            fi
            
            # Close boundaries
            echo -e "\n--RELATED_BOUNDARY_12345--" >> "$TMP_EML"
            echo -e "\n--WEBAPP_BOUNDARY_12345--" >> "$TMP_EML"
            
            # Update the HTML file with correct paths for local serving
            HTML_CONTENT=$(cat "$EXTRACTED_DIR/index.html")
            
            # Update paths in HTML
            UPDATED_HTML=$(echo "$HTML_CONTENT" | \
                sed 's|href="cid:style_css"|href="style.css"|g' | \
                sed 's|src="cid:script_js"|src="app.js"|g' | \
                sed 's|href="cid:favicon_svg"|href="favicon.svg"|g')
            
            # Add favicon link if it doesn't exist
            if ! echo "$UPDATED_HTML" | grep -q 'link.*favicon'; then
                UPDATED_HTML=$(echo "$UPDATED_HTML" | \
                    sed '/<head>/a \    <link rel="icon" type="image/svg+xml" href="images/favicon.svg">')
            fi
            
            # Save the updated HTML
            echo "$UPDATED_HTML" > extracted_content/index.html
            
            echo "Zawartość wyodrębniona do katalogu extracted_content/"
            ls -la extracted_content/
            ;;
        run)
            echo "Uruchamianie lokalnego serwera..."
            # Najpierw wyodrębnij, jeśli to konieczne
            if [ ! -d "extracted_content" ]; then
                "$0" extract
            fi
            # Uruchom prosty serwer HTTP
            echo "Aplikacja dostępna pod adresem: http://localhost:8000"
            cd extracted_content
            # Użyj Pythona z prostym serwerem HTTP z obsługą CORS
            python3 -c '
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

if __name__ == "__main__":
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print("Serwer działa pod adresem http://localhost:8000")
    httpd.serve_forever()
'
            ;;
        browse)
            echo "Otwieranie w przeglądarce..."
            xdg-open "http://localhost:8000" 2>/dev/null || open "http://localhost:8000" 2>/dev/null || echo "Nie udało się otworzyć przeglądarki"
            ;;
        info)
            echo "Informacje o skrypcie:"
            echo "- Nazwa: Faktury Maj 2025"
            echo "- Typ: Aplikacja webowa"
            echo "- Generator: EML-Script-Generator"
            ;;
    esac
    exit 0
fi

# Poniższa część jest ignorowana przez basha, ale jest częścią wiadomości EML
: '--EML_CONTENT_STARTS_HERE--
MIME-Version: 1.0'
Subject: WebApp - Faktury Maj 2025
Content-Type: multipart/mixed; boundary="WEBAPP_BOUNDARY_12345"
X-App-Type: docker-webapp
X-App-Name: Faktury Maj 2025
X-Generator: EML-Script-Generator

--WEBAPP_BOUNDARY_12345
Content-Type: text/html
Content-Disposition: inline; filename="index.html"
Content-Transfer-Encoding: quoted-printable

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

    <script type="module" src="js/app.js"></script>
</body>
</html>

--WEBAPP_BOUNDARY_12345
Content-Type: text/css
Content-Disposition: inline; filename="style.css"
Content-Transfer-Encoding: quoted-printable

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
Content-Type: image/svg+xml
Content-ID: <favicon_svg>
Content-Transfer-Encoding: base64
Content-Disposition: inline; filename="favicon.svg"

PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMzIiIGhl
aWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIw
MDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI2IiBmaWxsPSIjNGY0
NmVlIi8+CiAgPHBhdGggZD0iTTE2IDhMMjAgMTJIMTJMMTYgOFoiIGZpbGw9IndoaXRlIi8+CiAg
PHBhdGggZD0iTTEyIDE0SDIwVjIySDEyVjE0WiIgZmlsbD0id2hpdGUiLz4KICA8cGF0aCBkPSJN
OCAyNEgyNFYyNkg4VjI0WiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+Cg==

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
    "favicon.svg",
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