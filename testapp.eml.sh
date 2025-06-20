#!/bin/bash
#
# Self-extracting EML script - faktury-maj.eml.sh
# Użycie: ./faktury-maj.eml.sh [extract|run|browse|info]
#
# Ten plik jest jednocześnie:
# 1. Wykonywalnym skryptem bash
# 2. Płynym plikiem EML z załącznikami
#

# EML content starts here
MIME-Version: 1.0
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

    <script src="cid:script_js"></script>
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