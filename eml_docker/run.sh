#!/bin/bash
# Przykład tworzenia i używania samoekstraktującego się skryptu EML

echo "=== Tworzenie przykładowej aplikacji ==="

# 1. Utwórz katalog projektu
mkdir -p my-invoices-app
cd my-invoices-app

# 2. Utwórz podstawowy plik HTML
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moje Faktury</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>📋 Dashboard Faktur</h1>
        <div class="stats">
            <div class="card">
                <h3>Wszystkie faktury</h3>
                <span class="number">24</span>
            </div>
            <div class="card">
                <h3>Opłacone</h3>
                <span class="number">18</span>
            </div>
            <div class="card">
                <h3>Oczekujące</h3>
                <span class="number">6</span>
            </div>
        </div>

        <div class="invoice-list">
            <div class="invoice-item">
                <img src="invoice-thumb.jpg" alt="Faktura" class="thumb">
                <div class="info">
                    <h4>Faktura #2025/001</h4>
                    <p>ABC Company</p>
                    <span class="amount">1,250 PLN</span>
                </div>
            </div>
        </div>

        <button onclick="showAlert()">Test JavaScript</button>
    </div>

    <script src="app.js"></script>
</body>
</html>
EOF

# 3. Utwórz plik CSS
cat > style.css << 'EOF'
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #74b9ff, #0984e3);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

h1 {
    color: white;
    text-align: center;
    margin-bottom: 30px;
    font-size: 2.5em;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.card {
    background: rgba(255, 255, 255, 0.95);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
}

.card h3 {
    color: #2d3436;
    margin-bottom: 15px;
    font-size: 1.1em;
}

.number {
    font-size: 2.5em;
    font-weight: bold;
    color: #0984e3;
}

.invoice-list {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 20px;
    backdrop-filter: blur(10px);
}

.invoice-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    border-bottom: 1px solid #eee;
}

.thumb {
    width: 60px;
    height: 80px;
    object-fit: cover;
    border-radius: 8px;
    border: 2px solid #ddd;
}

.info h4 {
    color: #2d3436;
    margin-bottom: 5px;
}

.info p {
    color: #636e72;
    margin-bottom: 8px;
}

.amount {
    font-weight: bold;
    color: #00b894;
    font-size: 1.2em;
}

button {
    background: #00b894;
    color: white;
    border: none;
    padding: 12px 25px;
    border-radius: 25px;
    cursor: pointer;
    font-size: 1em;
    margin-top: 20px;
    transition: background 0.3s ease;
}

button:hover {
    background: #00a085;
}
EOF

# 4. Utwórz plik JavaScript
cat > app.js << 'EOF'
function showAlert() {
    alert('JavaScript działa! 🎉\n\nAplikacja została załadowana z pliku EML.');
}

// Animacja ładowania
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Aplikacja załadowana z EML+Dockerfile');

    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });

    // Pokaż informację o ładowaniu
    setTimeout(() => {
        const notice = document.createElement('div');
        notice.innerHTML = '🚀 Aplikacja uruchomiona z samoekstraktującego się skryptu EML!';
        notice.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #00b894;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 300px;
            animation: slideIn 0.5s ease;
        `;

        // CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(notice);

        // Usuń po 5 sekundach
        setTimeout(() => {
            notice.style.transition = 'all 0.5s ease';
            notice.style.transform = 'translateX(100%)';
            notice.style.opacity = '0';
            setTimeout(() => notice.remove(), 500);
        }, 5000);
    }, 2000);
});
EOF

# 5. Utwórz przykładową miniaturę faktury (placeholder image)
cat > invoice-thumb.jpg.base64 << 'EOF'
/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAoAFADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBSEGMUFRBxMiYXEUMoGRoQgjscHwFSNC0eEzFmLwNHKC8SVDNaUmZEU4SWNY/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAVEQEBAAAAAAAAAAAAAAAAAAAAAf/aAAwDAQACEQMRAD8A/T6iiigKKKKAooooP//Z
EOF
base64 -d invoice-thumb.jpg.base64 > invoice-thumb.jpg
rm invoice-thumb.jpg.base64

cd ..

echo "✅ Przykładowa aplikacja utworzona w katalogu: my-invoices-app/"

echo ""
echo "=== Generowanie samoekstraktującego się skryptu EML ==="

# 6. Uruchom generator
python3 eml_script_gen.py my-invoices-app/ my-invoices.eml.sh

echo ""
echo "=== Testowanie utworzonego skryptu ==="

# 7. Ustaw uprawnienia
chmod +x my-invoices.eml.sh

# 8. Pokaż informacje o pliku
echo "📁 Plik utworzony:"
ls -lh my-invoices.eml.sh

echo ""
echo "🔍 Informacje o zawartości:"
./my-invoices.eml.sh info

echo ""
echo "=== Instrukcje użytkowania ==="
echo ""
echo "Możesz teraz używać pliku my-invoices.eml.sh jako:"
echo ""
echo "1. 🌐 Aplikacja webowa:"
echo "   ./my-invoices.eml.sh browse"
echo ""
echo "2. 🐳 Container Docker:"
echo "   ./my-invoices.eml.sh run"
echo ""
echo "3. 📂 Wyodrębnienie plików:"
echo "   ./my-invoices.eml.sh extract"
echo ""
echo "4. 📧 Plik email (otwórz w Thunderbird/Outlook):"
echo "   thunderbird my-invoices.eml.sh"
echo ""
echo "5. 📤 Wysyłanie przez email:"
echo "   mail -a my-invoices.eml.sh recipient@example.com"
echo ""
echo "6. 🔍 Przeglądanie zawartości:"
echo "   strings my-invoices.eml.sh | grep 'Content-Type'"
echo ""
echo "=== Zalety tego podejścia ==="
echo "✅ Jeden plik zawiera wszystko (HTML, CSS, JS, obrazy, Dockerfile)"
echo "✅ Executable skrypt bash + prawidłowy plik EML"
echo "✅ Brak base64 overhead dla niektórych plików"
echo "✅ Możliwość wysyłania jako załącznik email"
echo "✅ Self-contained - nie wymaga dodatkowych narzędzi"
echo "✅ Cross-platform kompatybilność"
echo "✅ Docker ready - natychmiastowe deployment"
echo ""
echo "=== Test szybki ==="
echo "Spróbuj teraz:"
echo "  ./my-invoices.eml.sh browse"
EOF