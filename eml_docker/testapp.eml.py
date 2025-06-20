#!/usr/bin/env python3
"""
Generator samoekstraktujących się skryptów EML
Użycie: python eml_script_gen.py source_dir/ output.eml.sh
"""

import os
import sys
import base64
import mimetypes
from pathlib import Path
import json
from datetime import datetime


class EMLScriptGenerator:
    def __init__(self, source_dir, output_file):
        self.source_dir = Path(source_dir)
        self.output_file = output_file
        self.boundary = "WEBAPP_BOUNDARY_12345"
        self.content_ids = {}

    def get_bash_header(self):
        """Generuje nagłówek bash skryptu"""
        script_name = Path(self.output_file).name
        return f'''#!/bin/bash
#
# Self-extracting EML script - {script_name}
# Użycie: ./{script_name} [extract|run|browse|info]
#
# Ten plik jest jednocześnie:
# 1. Wykonywalnym skryptem bash
# 2. Prawidłowym plikiem EML z załącznikami
#

# Jeśli uruchomiono jako skrypt, obsłuż parametry
if [ "$0" = "${{BASH_SOURCE[0]}}" ]; then
    ACTION="${{1:-browse}}"
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

with open('$TEMP_DIR/content.eml', 'rb') as f:
    msg = email.message_from_binary_file(f)

extracted = []
for part in msg.walk():
    if part.get_content_maintype() == 'multipart':
        continue

    filename = part.get_param('filename', header='content-disposition')
    if not filename:
        content_type = part.get_content_type()
        if content_type == 'text/html':
            filename = 'index.html'
        elif content_type == 'text/css':
            filename = 'style.css'
        elif content_type == 'application/javascript':
            filename = 'script.js'
        elif 'dockerfile' in content_type.lower():
            filename = 'Dockerfile'
        else:
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
        print(f'✓ {{filename}} ({{len(content)}} bytes)')

    except Exception as e:
        print(f'✗ Error extracting {{filename}}: {{e}}')

print(f'Extracted to: $TEMP_DIR')
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

            if [ -f "$TEMP_DIR/index.html" ]; then
                # Zamień Content-ID references na lokalne pliki
                python3 -c "
import re
import os

html_file = '$TEMP_DIR/index.html'
with open(html_file, 'r') as f:
    content = f.read()

# Zamień cid: references na lokalne pliki
content = re.sub(r'src=[\"\\\\\\']cid:([^\"\\\\\\'>]+)[\"\\\\\\']', r'src=\\\"\\\\1\\\"', content)
content = re.sub(r'href=[\"\\\\\\']cid:([^\"\\\\\\'>]+)[\"\\\\\\']', r'href=\\\"\\\\1\\\"', content)

with open(html_file, 'w') as f:
    f.write(content)
"

                # Otwórz w przeglądarce
                if command -v xdg-open > /dev/null; then
                    xdg-open "file://$TEMP_DIR/index.html"
                elif command -v open > /dev/null; then
                    open "file://$TEMP_DIR/index.html"
                else
                    echo "Otwórz w przeglądarce: file://$TEMP_DIR/index.html"
                fi
            else
                echo "Błąd: Brak index.html w EML"
                exit 1
            fi
            ;;

        "info")
            echo "Informacje o EML webapp:"
            echo "Plik: $SCRIPT_FILE"
            echo "Rozmiar: $(du -h "$SCRIPT_FILE" | cut -f1)"

            # Pokaż nagłówki EML
            EML_START=$(grep -n "^MIME-Version:" "$SCRIPT_FILE" | head -1 | cut -d: -f1)
            if [ -n "$EML_START" ]; then
                echo "EML Headers:"
                sed -n "${{EML_START}},/^$/p" "$SCRIPT_FILE" | head -10
            fi

            # Policz załączniki
            ATTACHMENTS=$(grep -c "Content-Disposition: attachment" "$SCRIPT_FILE" 2>/dev/null || echo "0")
            echo "Załączniki: $ATTACHMENTS"
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

'''

    def get_eml_headers(self):
        """Generuje nagłówki EML"""
        return f'''MIME-Version: 1.0
Subject: WebApp - {self.source_dir.name}
Content-Type: multipart/mixed; boundary="{self.boundary}"
X-App-Type: docker-webapp
X-App-Name: {self.source_dir.name}
X-Generator: EML-Script-Generator
X-Created: {datetime.now().isoformat()}

'''

    def encode_file_content(self, file_path, is_binary=False):
        """Koduje zawartość pliku"""
        with open(file_path, 'rb') as f:
            content = f.read()

        if is_binary:
            # Base64 dla binarnych
            encoded = base64.b64encode(content).decode('ascii')
            # Złam linie co 76 znaków (RFC standard)
            wrapped = '\n'.join(encoded[i:i + 76] for i in range(0, len(encoded), 76))
            return wrapped, 'base64'
        else:
            # Quoted-printable dla tekstu
            try:
                text_content = content.decode('utf-8')
                # Podstawowe quoted-printable (dla prostoty)
                encoded = text_content.replace('=', '=3D').replace('\n', '\n')
                return encoded, 'quoted-printable'
            except UnicodeDecodeError:
                # Fallback do base64 jeśli nie da się zdekodować jako UTF-8
                encoded = base64.b64encode(content).decode('ascii')
                wrapped = '\n'.join(encoded[i:i + 76] for i in range(0, len(encoded), 76))
                return wrapped, 'base64'

    def generate_content_id(self, filename):
        """Generuje Content-ID dla pliku"""
        # Zamień rozszerzenie i znaki specjalne
        clean_name = filename.replace('.', '_').replace('-', '_').replace(' ', '_')
        content_id = f"<{clean_name}>"
        self.content_ids[filename] = content_id
        return content_id

    def process_html_file(self, file_path):
        """Przetwarza plik HTML i zamienia lokalne referencje na Content-ID"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Zamień lokalne referencje na cid:
        for filename, content_id in self.content_ids.items():
            cid_ref = f"cid:{content_id[1:-1]}"  # Usuń < >
            content = content.replace(f'src="{filename}"', f'src="{cid_ref}"')
            content = content.replace(f"src='{filename}'", f"src='{cid_ref}'")
            content = content.replace(f'href="{filename}"', f'href="{cid_ref}"')
            content = content.replace(f"href='{filename}'", f"href='{cid_ref}'")

        return content

    def add_file_to_eml(self, file_path, output):
        """Dodaje plik do EML jako część MIME"""
        filename = file_path.name
        mimetype, _ = mimetypes.guess_type(str(file_path))

        if not mimetype:
            mimetype = 'application/octet-stream'

        # Określ czy plik jest binarny
        is_binary = not mimetype.startswith('text/')

        # Generuj Content-ID dla referencji
        content_id = self.generate_content_id(filename)

        # Koduj zawartość
        if filename.endswith('.html'):
            # Specjalne przetwarzanie dla HTML
            processed_content = self.process_html_file(file_path)
            encoded_content = processed_content.replace('=', '=3D')
            encoding = 'quoted-printable'
        else:
            encoded_content, encoding = self.encode_file_content(file_path, is_binary)

        # Napisz część MIME
        output.write(f"--{self.boundary}\n")
        output.write(f"Content-Type: {mimetype}")

        if mimetype.startswith('text/'):
            output.write("; charset=utf-8")
        output.write("\n")

        # Content-ID dla referencji w HTML
        if not filename.endswith('.html'):  # HTML nie potrzebuje Content-ID
            output.write(f"Content-ID: {content_id}\n")

        output.write(f"Content-Transfer-Encoding: {encoding}\n")

        # Content-Disposition
        if filename.endswith('.html'):
            output.write(f'Content-Disposition: inline; filename="{filename}"\n')
        else:
            output.write(f'Content-Disposition: attachment; filename="{filename}"\n')

        output.write("\n")  # Pusta linia przed zawartością
        output.write(encoded_content)
        output.write("\n\n")

    def create_dockerfile_if_missing(self):
        """Tworzy domyślny Dockerfile jeśli nie istnieje"""
        dockerfile_path = self.source_dir / 'Dockerfile'
        if not dockerfile_path.exists():
            dockerfile_content = '''FROM nginx:alpine

# Kopiuj wszystkie pliki do nginx
COPY *.html /usr/share/nginx/html/
COPY *.css /usr/share/nginx/html/
COPY *.js /usr/share/nginx/html/
COPY *.jpg /usr/share/nginx/html/
COPY *.png /usr/share/nginx/html/
COPY *.gif /usr/share/nginx/html/
COPY *.pdf /usr/share/nginx/html/

# Konfiguracja nginx dla SPA
RUN echo 'server { \\
    listen 80; \\
    server_name localhost; \\
    root /usr/share/nginx/html; \\
    index index.html; \\
    \\
    location / { \\
        try_files $uri $uri/ /index.html; \\
    } \\
    \\
    # Cache static assets \\
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|pdf)$ { \\
        expires 1y; \\
        add_header Cache-Control "public, immutable"; \\
    } \\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]'''

            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            print(f"✓ Utworzono domyślny Dockerfile")

    def create_metadata_file(self):
        """Tworzy plik metadata.json"""
        files = [f.name for f in self.source_dir.iterdir() if f.is_file()]

        metadata = {
            "name": self.source_dir.name,
            "version": "1.0.0",
            "description": f"WebApp {self.source_dir.name}",
            "type": "webapp-eml-script",
            "created": datetime.now().isoformat(),
            "files": files,
            "generator": "EML-Script-Generator"
        }

        metadata_path = self.source_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"✓ Utworzono metadata.json")

    def build(self):
        """Buduje samoekstraktujący się skrypt EML"""
        print(f"Budowanie EML Script z: {self.source_dir}")

        # Utwórz brakujące pliki
        self.create_dockerfile_if_missing()
        self.create_metadata_file()

        # Najpierw przejdź przez wszystkie pliki, żeby wygenerować Content-IDs
        for file_path in sorted(self.source_dir.iterdir()):
            if file_path.is_file() and not file_path.name.startswith('.'):
                if not file_path.name.endswith('.html'):  # HTML nie dostaje Content-ID
                    self.generate_content_id(file_path.name)

        with open(self.output_file, 'w', encoding='utf-8') as output:
            # Napisz nagłówek bash
            output.write(self.get_bash_header())

            # Napisz nagłówki EML
            output.write(self.get_eml_headers())

            # Dodaj pliki w określonej kolejności
            file_order = ['index.html', '*.css', '*.js', '*.jpg', '*.png', '*.gif', '*.pdf', 'Dockerfile',
                          'metadata.json']
            processed_files = set()

            # Przetwórz pliki w określonej kolejności
            for pattern in file_order:
                if '*' in pattern:
                    # Glob pattern
                    ext = pattern[1:]  # usuń *
                    matching_files = [f for f in self.source_dir.iterdir()
                                      if f.is_file() and f.name.endswith(ext)]
                    for file_path in sorted(matching_files):
                        if file_path.name not in processed_files:
                            self.add_file_to_eml(file_path, output)
                            processed_files.add(file_path.name)
                            print(f"✓ Dodano: {file_path.name}")
                else:
                    # Konkretny plik
                    file_path = self.source_dir / pattern
                    if file_path.exists() and file_path.name not in processed_files:
                        self.add_file_to_eml(file_path, output)
                        processed_files.add(file_path.name)
                        print(f"✓ Dodano: {file_path.name}")

            # Dodaj pozostałe pliki
            for file_path in sorted(self.source_dir.iterdir()):
                if (file_path.is_file() and
                        not file_path.name.startswith('.') and
                        file_path.name not in processed_files):
                    self.add_file_to_eml(file_path, output)
                    processed_files.add(file_path.name)
                    print(f"✓ Dodano: {file_path.name}")

            # Zakończ multipart
            output.write(f"--{self.boundary}--\n")

        # Ustaw uprawnienia wykonywania
        os.chmod(self.output_file, 0o755)

        file_size = os.path.getsize(self.output_file)
        print(f"\n✅ EML Script utworzony: {self.output_file}")
        print(f"📁 Rozmiar: {file_size:,} bajtów ({file_size / 1024:.1f} KB)")
        print(f"📦 Plików: {len(processed_files)}")

        print(f"\nUżycie:")
        print(f"  chmod +x {self.output_file}")
        print(f"  ./{self.output_file} browse  # Otwórz w przeglądarce")
        print(f"  ./{self.output_file} run     # Uruchom Docker container")
        print(f"  ./{self.output_file} extract # Wyodrębnij pliki")
        print(f"  ./{self.output_file} info    # Pokaż informacje")


def main():
    if len(sys.argv) != 3:
        print("Użycie: python eml_script_gen.py <katalog_źródłowy> <output.eml.sh>")
        print("")
        print("Przykład:")
        print("  python eml_script_gen.py my-webapp/ webapp.eml.sh")
        print("  chmod +x webapp.eml.sh")
        print("  ./webapp.eml.sh browse")
        sys.exit(1)

    source_dir = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(source_dir):
        print(f"Błąd: Katalog '{source_dir}' nie istnieje")
        sys.exit(1)

    if not output_file.endswith('.eml.sh'):
        print("Ostrzeżenie: Zalecane rozszerzenie .eml.sh")

    generator = EMLScriptGenerator(source_dir, output_file)
    generator.build()


if __name__ == '__main__':
    main()