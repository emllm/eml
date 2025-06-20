                echo "Znaleziono plik JavaScript, wyodrębniam..."
                mkdir -p extracted_content/js
                # Pobierz zawartość między znacznikami Content-Type a następnym --WEBAPP_BOUNDARY_
                # i wyciągnij tylko kod JavaScript (pomijając nagłówki i linie poleceń)
                awk '/Content-Type: application\/javascript/{ 
                    while(getline) { 
                        if(/^--WEBAPP_BOUNDARY_/) exit; 
                        if(!/^Content-/ && !/^\s*$/) print; 
                    } 
                }' "$0" > extracted_content/js/app.js
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
            # Utwórz kopię oryginalnego pliku EML
            cp "$0" extracted_content/original.eml
            # Zapisz oryginalną zawartość HTML
            HTML_CONTENT=$(cat extracted_content/index.html)
            # Zaktualizuj ścieżki w HTML
            UPDATED_HTML=$(echo "$HTML_CONTENT" | \
                sed 's|href="cid:style_css"|href="css/style.css"|g' | \
                sed 's|src="cid:script_js"|src="js/app.js"|g')
            # Dodaj link do favicon, jeśli nie istnieje
            if ! echo "$UPDATED_HTML" | grep -q 'link.*favicon'; then
                UPDATED_HTML=$(echo "$UPDATED_HTML" | \
                    sed '/<head>/a \    <link rel="icon" type="image/svg+xml" href="images/favicon.svg">')
            fi
            # Zapisz zaktualizowany HTML
            echo "$UPDATED_HTML" > extracted_content/index.html
            # Przygotuj oryginalną wersję HTML dla pliku EML
            ORIGINAL_HTML=$(echo "$UPDATED_HTML" | \
                sed 's|href="css/style.css"|href="cid:style_css"|g' | \
                sed 's|src="js/app.js"|src="cid:script_js"|g')
            # Zaktualizuj oryginalny plik EML z oryginalnymi ścieżkami
            awk -v html="$ORIGINAL_HTML" '{
                if ($0 ~ /^<!DOCTYPE html>/) { in_html=1; print html; next }
                if (in_html && $0 ~ /<\/html>/) { in_html=0; next }
                if (!in_html) print $0
            }' extracted_content/original.eml > extracted_content/original.eml.tmp && \
            mv extracted_content/original.eml.tmp extracted_content/original.eml
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
X-App-Type: docker-webapp
X-App-Name: Faktury Maj 2025
X-Generator: EML-Script-Generator
