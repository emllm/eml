                echo "Znaleziono plik JavaScript, wyodrębniam..."
                JS_END=$(tail -n +"$JS_START" "$0" | grep -n -m 1 '^--WEBAPP_BOUNDARY_' | cut -d: -f1)
                JS_END=$((JS_START + JS_END - 1))
                head -n "$JS_END" "$0" | tail -n +"$JS_START" | \
                    grep -v '^Content-' | \
                    grep -v '^--' | \
                    grep -v '^[[:space:]]*EOM' | \
                    grep -v '^[[:space:]]*cat ' | \
                    grep -v '^[[:space:]]*fi' | \
                    grep -v '^[[:space:]]*#' > extracted_content/app.js
                sed -i '/^[[:space:]]*$/d' extracted_content/app.js
                echo "Znaleziono favicon, wyodrębniam..."
                    grep -v '^Content-' | \
                    base64 -d > extracted_content/favicon.svg 2>/dev/null || \
                    grep -v '^Content-' > extracted_content/favicon.svg
            mkdir -p extracted_content
            echo "Tworzenie wersji HTML z referencjami CID..."
                sed 's|href="css/style.css"|href="cid:style_css"|g' | \
                sed 's|src="js/app.js"|src="cid:script_js"|g' | \
                sed 's|href="images/favicon.svg"|href="cid:favicon_svg"|g' > extracted_content/cid_index.html
            TMP_EML=$(mktemp)
MIME-Version: 1.0
From: system@example.com
To: recipient@example.com
Subject: WebApp - Faktury Maj 2025
X-App-Type: docker-webapp
X-App-Name: Faktury Maj 2025
X-Generator: EML-Script-Generator
