#!/bin/bash

# Set the output directory
EXTRACT_DIR="$(pwd)/webapp"

# Create output directory
mkdir -p "$EXTRACT_DIR"

# Create index.html
cat > "$EXTRACT_DIR/index.html" << 'HTML_EOF'
<!DOCTYPE html>
<html lang="pl">
<head>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Faktur - Maj 2025</title>
    <link rel="stylesheet" href="style.css">
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
                <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNlZWVlZWUiLz4KICA8dGV4dCB4PSI1MCIgeT0iNTUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+RmFrdHVyYSAjMTwvdGV4dD4KPC9zdmc+" alt="Faktura 001" class="thumbnail">
                <div class="invoice-info">
                    <h4>Faktura #2025/05/001</h4>
                    <p>Firma ABC Sp. z o.o.</p>
                    <span class="amount">2,500 PLN</span>
                    <span class="status paid">Opłacona</span>
                </div>
            </div>

            <div class="invoice-card" data-status="pending">
                <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNlZWVlZWUiLz4KICA8dGV4dCB4PSI1MCIgeT0iNTUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+RmFrdHVyYSAjMjwvdGV4dD4KPC9zdmc+" alt="Faktura 002" class="thumbnail">
                <div class="invoice-info">
                    <h4>Faktura #2025/05/002</h4>
                    <p>XYZ Solutions</p>
                    <span class="amount">1,200 PLN</span>
                    <span class="status pending">Oczekuje</span>
                </div>
            </div>
        </div>
    </main>

    <script src="app.js"></script>
</body>
</html>
HTML_EOF

# Create style.css
cat > "$EXTRACT_DIR/style.css" << 'CSS_EOF'
:root {
    --primary-color: #4a6fa5;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --light-bg: #f8f9fa;
    --dark-bg: #343a40;
    --border-radius: 8px;
    --box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f7fa;
    padding: 20px;
}

header {
    background-color: white;
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
}

h1 {
    color: var(--primary-color);
    margin-bottom: 10px;
    font-size: 1.8rem;
}

nav button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 8px 16px;
    margin: 5px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

nav button:hover {
    background-color: #3a5a80;
}

.stats {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    flex: 1;
    min-width: 200px;
}

.stat-card h3 {
    color: var(--secondary-color);
    font-size: 1rem;
    margin-bottom: 10px;
}

.amount {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}

.count {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--success-color);
}

.invoice-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.invoice-card {
    background: white;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--box-shadow);
    transition: transform 0.3s, box-shadow 0.3s;
    display: flex;
    flex-direction: column;
}

.invoice-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.thumbnail {
    width: 100%;
    height: 150px;
    object-fit: cover;
}

.invoice-info {
    padding: 15px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.invoice-info h4 {
    margin: 0 0 5px 0;
    color: var(--primary-color);
}

.invoice-info p {
    color: var(--secondary-color);
    margin: 0 0 10px 0;
    flex-grow: 1;
}

.status {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    margin-top: 5px;
}

.status.paid {
    background-color: #d4edda;
    color: #155724;
}

.status.pending {
    background-color: #fff3cd;
    color: #856404;
}

/* Responsywność */
@media (max-width: 768px) {
    .stats {
        flex-direction: column;
    }
    
    .invoice-grid {
        grid-template-columns: 1fr;
    }
    
    header {
        flex-direction: column;
        text-align: center;
    }
    
    nav {
        margin-top: 15px;
    }
}
CSS_EOF

# Create app.js
cat > "$EXTRACT_DIR/app.js" << 'JS_EOF'
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

# Create favicon.svg
cat > "$EXTRACT_DIR/favicon.svg" << 'SVG_EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#4a6fa5" rx="10"/>
  <text x="50" y="60" font-family="Arial" font-size="40" fill="white" text-anchor="middle">$</text>
</svg>
SVG_EOF

# Function to start the web server
start_server() {
    echo "Starting web server..."
    echo "Web application available at: http://localhost:8080"
    echo "Press Ctrl+C to stop the server"
    cd "$EXTRACT_DIR"
    python3 -m http.server 8080
}

# Main script
case "$1" in
    run)
        start_server
        ;;
    *)
        echo "Web application files extracted to: $EXTRACT_DIR"
        echo "To run the web server, use: $0 run"
        ;;
esac
