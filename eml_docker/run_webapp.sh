#!/bin/bash

# Create a temporary directory for the webapp
TEMP_DIR=$(mktemp -d)
echo "Extracting webapp to: $TEMP_DIR"

# Create the webapp files
cat > "$TEMP_DIR/index.html" << 'HTML_EOF'
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Faktury Maj 2025</title>
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
                <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNlZWVlZWUiLz48dGV4dCB4PSI1MCIgeT0iNTUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+RmFrdHVyYSAjMTwvdGV4dD48L3N2Zz4=" alt="Faktura 001" class="thumbnail">
                <div class="invoice-info">
                    <h4>Faktura #2025/05/001</h4>
                    <p>Firma ABC Sp. z o.o.</p>
                    <span class="amount">2,500 PLN</span>
                    <span class="status paid">Opłacona</span>
                </div>
            </div>

            <div class="invoice-card" data-status="pending">
                <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNlZWVlZWUiLz48dGV4dCB4PSI1MCIgeT0iNTUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+RmFrdHVyYSAjMjwvdGV4dD48L3N2Zz4=" alt="Faktura 002" class="thumbnail">
                <div class="invoice-info">
                    <h4>Faktura #2025/05/002</h4>
                    <p>XYZ Solutions</p>
                    <span class="amount">1,200 PLN</span>
                    <span class="status pending">Oczekuje</span>
                </div>
            </div>
        </div>
    </main>
    <script src="script.js"></script>
</body>
</html>
HTML_EOF

# Create style.css
cat > "$TEMP_DIR/style.css" << 'CSS_EOF'
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
    background: white;
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    margin-bottom: 20px;
}

h1 {
    color: var(--primary-color);
    margin-bottom: 10px;
}

nav {
    margin-top: 15px;
}

nav button {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 8px 16px;
    margin-right: 10px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

nav button:hover {
    background: #3a5a80;
}

.stats {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    flex: 1;
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
}

.invoice-card {
    background: white;
    border-radius: var(--border-radius);
    padding: 15px;
    box-shadow: var(--box-shadow);
    display: flex;
    gap: 15px;
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

.invoice-info {
    flex: 1;
}

.invoice-info h4 {
    color: var(--primary-color);
    margin-bottom: 5px;
}

.invoice-info p {
    color: var(--secondary-color);
    margin-bottom: 10px;
}

.status {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
}

.status.paid {
    background: #d4edda;
    color: #155724;
}

.status.pending {
    background: #fff3cd;
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
}
CSS_EOF

# Create script.js
cat > "$TEMP_DIR/script.js" << 'JS_EOF'
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

# Start the web server
echo "Starting web server on port 8080..."
echo "Web application available at: http://localhost:8080"
echo "Press Ctrl+C to stop the server"

# Start Python HTTP server in the background
cd "$TEMP_DIR"
python3 -m http.server 8080
