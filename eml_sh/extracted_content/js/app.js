                # Znajdź pozycję początku i końca sekcji JavaScript
                JS_START=$(grep -n 'Content-Type: application/javascript' "$0" | head -1 | cut -d: -f1)
                JS_END=$(tail -n +"$JS_START" "$0" | grep -n -m 1 '^--WEBAPP_BOUNDARY_' | cut -d: -f1)
                JS_END=$((JS_START + JS_END - 1))
                # Wyodrębnij tylko kod JavaScript, pomiń 3 pierwsze linie (nagłówki)
                tail -n +"$((JS_START + 3))" "$0" | head -n "$((JS_END - JS_START - 4))" > extracted_content/js/app.js
            fi
            
            # Wyodrębnij favicon
            if grep -q 'Content-Type: image/svg+xml.*favicon' "$0"; then
                echo "Znaleziono favicon, wyodrębniam..."
                mkdir -p extracted_content/images
                sed -n '/Content-Type: image\/svg\+xml.*favicon/,/--WEBAPP_BOUNDARY_/p' "$0" | \
                    grep -v '^Content-' | \
                    base64 -d > extracted_content/images/favicon.svg 2>/dev/null || \
                    sed -n '/Content-Type: image\/svg\+xml.*favicon/,/--WEBAPP_BOUNDARY_/p' "$0" | \
                    grep -v '^Content-' > extracted_content/images/favicon.svg
            fi
            
            # Utwórz plik original.eml z prawidłowymi nagłówkami wiadomości
            cat > extracted_content/original.eml << 'EOL'
MIME-Version: 1.0
From: system@example.com
To: recipient@example.com
Subject: WebApp - Faktury Maj 2025
X-App-Type: docker-webapp
X-App-Name: Faktury Maj 2025
X-Generator: EML-Script-Generator
Content-Type: multipart/mixed; boundary="WEBAPP_BOUNDARY_12345"
