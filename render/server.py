#!/usr/bin/env python3
"""
Serwer Flask do renderowania plików EML do HTML/PNG
Własna implementacja Docker API
"""

from flask import Flask, request, jsonify, render_template_string, send_file
import email
from email.parser import BytesParser
from email import policy
import os
import tempfile
import subprocess
import uuid
import json
import html
from pathlib import Path
import logging
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Katalogi robocze
UPLOAD_DIR = "/app/uploads"
OUTPUT_DIR = "/app/outputs"
TEMP_DIR = "/app/temp"

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)


class EMLProcessor:
    def __init__(self):
        self.parsed_message = None

    def load_eml_content(self, content):
        """Wczytuje zawartość EML z bytes"""
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')
            self.parsed_message = BytesParser(policy=policy.default).parsebytes(content)
            return True
        except Exception as e:
            logger.error(f"Błąd parsowania EML: {e}")
            return False

    def validate_eml(self):
        """Waliduje strukturę EML"""
        if not self.parsed_message:
            return False, ["Brak wczytanej wiadomości"]

        issues = []
        required_headers = ['From', 'To', 'Subject']

        for header in required_headers:
            if not self.parsed_message.get(header):
                issues.append(f"Brak nagłówka: {header}")

        if self.parsed_message.defects:
            for defect in self.parsed_message.defects:
                issues.append(f"Defekt struktury: {defect}")

        return len(issues) == 0, issues

    def extract_content(self):
        """Wyodrębnia zawartość wiadomości"""
        if not self.parsed_message:
            return None

        content = {
            'headers': dict(self.parsed_message.items()),
            'text_body': '',
            'html_body': '',
            'attachments': []
        }

        if self.parsed_message.is_multipart():
            for part in self.parsed_message.walk():
                content_type = part.get_content_type()

                if content_type == 'text/plain':
                    content['text_body'] = part.get_content()
                elif content_type == 'text/html':
                    content['html_body'] = part.get_content()
                elif part.get_filename():
                    content['attachments'].append({
                        'filename': part.get_filename(),
                        'content_type': content_type,
                        'size': len(part.get_payload(decode=True) or b'')
                    })
        else:
            if self.parsed_message.get_content_type() == 'text/html':
                content['html_body'] = self.parsed_message.get_content()
            else:
                content['text_body'] = self.parsed_message.get_content()

        return content

    def render_to_html(self):
        """Renderuje EML do HTML"""
        content = self.extract_content()
        if not content:
            return None

        is_valid, issues = self.validate_eml()

        html_template = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EML Viewer</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .status-valid { background-color: rgba(72, 187, 120, 0.3); }
        .status-invalid { background-color: rgba(245, 101, 101, 0.3); }
        .headers {
            padding: 30px;
            border-bottom: 1px solid #e2e8f0;
        }
        .header-item {
            display: flex;
            margin-bottom: 12px;
            padding: 8px 0;
        }
        .header-label {
            font-weight: 600;
            color: #4a5568;
            width: 120px;
            flex-shrink: 0;
        }
        .header-value {
            flex-grow: 1;
            word-break: break-word;
        }
        .content-section {
            padding: 30px;
        }
        .content-body {
            background-color: #f8f9fb;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            margin-top: 15px;
            max-height: 500px;
            overflow-y: auto;
        }
        .attachments {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }
        .attachment {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            align-items: center;
        }
        .attachment-icon {
            width: 40px;
            height: 40px;
            background: #667eea;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 15px;
        }
        .issues {
            background: #fed7d7;
            border: 1px solid #feb2b2;
            border-radius: 6px;
            padding: 15px;
            margin: 20px 0;
        }
        .issues h4 {
            margin: 0 0 10px 0;
            color: #c53030;
        }
        .issues ul {
            margin: 0;
            padding-left: 20px;
        }
        h1, h2, h3 { margin-top: 0; }
        h2 { color: #2d3748; font-size: 20px; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .timestamp {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-section">
            <div class="status-badge {{ 'status-valid' if is_valid else 'status-invalid' }}">
                {{ '✓ Poprawna struktura' if is_valid else '⚠ Problemy ze strukturą' }}
            </div>
            <h1>📧 Podgląd wiadomości EML</h1>
            <div class="timestamp">Wygenerowano: {{ timestamp }}</div>
        </div>

        {% if not is_valid %}
        <div class="issues">
            <h4>Znalezione problemy:</h4>
            <ul>
                {% for issue in issues %}
                <li>{{ issue }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        <div class="headers">
            <h2>📋 Nagłówki wiadomości</h2>
            {% for key, value in headers.items() %}
            <div class="header-item">
                <div class="header-label">{{ key }}:</div>
                <div class="header-value">{{ value }}</div>
            </div>
            {% endfor %}
        </div>

        <div class="content-section">
            <h2>📝 Treść wiadomości</h2>

            {% if html_body %}
            <h3>Wersja HTML:</h3>
            <div class="content-body">
                {{ html_body | safe }}
            </div>
            {% endif %}

            {% if text_body %}
            <h3>Wersja tekstowa:</h3>
            <div class="content-body">
                <pre>{{ text_body }}</pre>
            </div>
            {% endif %}

            {% if not html_body and not text_body %}
            <p>Brak treści do wyświetlenia</p>
            {% endif %}
        </div>

        {% if attachments %}
        <div class="attachments">
            <h2>📎 Załączniki ({{ attachments | length }})</h2>
            {% for attachment in attachments %}
            <div class="attachment">
                <div class="attachment-icon">📄</div>
                <div>
                    <strong>{{ attachment.filename }}</strong><br>
                    <small>{{ attachment.content_type }} • {{ attachment.size }} bajtów</small>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
        """

        from jinja2 import Template
        template = Template(html_template)

        return template.render(
            headers=content['headers'],
            html_body=content['html_body'],
            text_body=content['text_body'],
            attachments=content['attachments'],
            is_valid=is_valid,
            issues=issues,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )


def html_to_png(html_content, output_path):
    """Konwertuje HTML do PNG używając wkhtmltoimage"""
    try:
        # Zapisz HTML do pliku tymczasowego
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_temp_path = f.name

        # Uruchom wkhtmltoimage
        cmd = [
            'wkhtmltoimage',
            '--width', '1024',
            '--height', '768',
            '--format', 'png',
            '--enable-local-file-access',
            '--javascript-delay', '1000',
            html_temp_path,
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Posprzątaj
        os.unlink(html_temp_path)

        if result.returncode == 0:
            return True, "Konwersja zakończona sukcesem"
        else:
            return False, f"Błąd wkhtmltoimage: {result.stderr}"

    except Exception as e:
        return False, f"Błąd konwersji: {str(e)}"


# Endpointy API
@app.route('/', methods=['GET'])
def index():
    """Strona główna z formularzem"""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>EML Renderer</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .upload-form { border: 2px dashed #ccc; padding: 40px; text-align: center; border-radius: 10px; }
        .upload-form:hover { border-color: #007bff; }
        input[type="file"] { margin: 20px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .info { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>🚀 EML Renderer API</h1>

    <div class="upload-form">
        <h2>📤 Wyślij plik EML</h2>
        <form action="/render" method="post" enctype="multipart/form-data">
            <input type="file" name="eml_file" accept=".eml" required>
            <br>
            <label>
                <input type="radio" name="output_format" value="html" checked> HTML
                <input type="radio" name="output_format" value="png"> PNG
            </label>
            <br>
            <button type="submit">🎨 Renderuj</button>
        </form>
    </div>

    <div class="info">
        <h3>📚 API Endpoints:</h3>
        <ul>
            <li><code>POST /render</code> - Renderuje plik EML</li>
            <li><code>POST /api/validate</code> - Waliduje plik EML</li>
            <li><code>GET /api/health</code> - Status serwera</li>
        </ul>

        <h3>💡 Przykład użycia curl:</h3>
        <pre>curl -X POST -F "eml_file=@plik.eml" -F "output_format=png" http://localhost:5000/render</pre>
    </div>
</body>
</html>
    """)


@app.route('/render', methods=['POST'])
def render_eml():
    """Renderuje plik EML do HTML lub PNG"""
    if 'eml_file' not in request.files:
        return jsonify({'error': 'Brak pliku EML'}), 400

    file = request.files['eml_file']
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400

    output_format = request.form.get('output_format', 'html')

    try:
        # Wczytaj i przetwórz EML
        eml_content = file.read()
        processor = EMLProcessor()

        if not processor.load_eml_content(eml_content):
            return jsonify({'error': 'Nie można sparsować pliku EML'}), 400

        # Walidacja
        is_valid, issues = processor.validate_eml()

        # Renderuj do HTML
        html_content = processor.render_to_html()
        if not html_content:
            return jsonify({'error': 'Nie można wyrenderować zawartości'}), 500

        if output_format == 'html':
            # Zwróć HTML
            return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}

        elif output_format == 'png':
            # Konwertuj do PNG
            unique_id = str(uuid.uuid4())
            png_path = os.path.join(OUTPUT_DIR, f'{unique_id}.png')

            success, message = html_to_png(html_content, png_path)

            if success:
                return send_file(png_path, mimetype='image/png', as_attachment=True,
                                 download_name=f'{file.filename}.png')
            else:
                return jsonify({'error': f'Błąd konwersji do PNG: {message}'}), 500

        else:
            return jsonify({'error': 'Nieobsługiwany format wyjściowy'}), 400

    except Exception as e:
        logger.error(f"Błąd renderowania: {e}")
        return jsonify({'error': f'Błąd serwera: {str(e)}'}), 500


@app.route('/api/validate', methods=['POST'])
def validate_eml():
    """Waliduje plik EML"""
    if 'eml_file' not in request.files:
        return jsonify({'error': 'Brak pliku EML'}), 400

    file = request.files['eml_file']
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400

    try:
        eml_content = file.read()
        processor = EMLProcessor()

        if not processor.load_eml_content(eml_content):
            return jsonify({
                'valid': False,
                'error': 'Nie można sparsować pliku EML',
                'issues': ['Błąd parsowania struktury']
            }), 400

        is_valid, issues = processor.validate_eml()
        content = processor.extract_content()

        result = {
            'valid': is_valid,
            'issues': issues,
            'summary': {
                'headers_count': len(content['headers']) if content else 0,
                'has_html_body': bool(content['html_body']) if content else False,
                'has_text_body': bool(content['text_body']) if content else False,
                'attachments_count': len(content['attachments']) if content else 0
            }
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Błąd walidacji: {e}")
        return jsonify({
            'valid': False,
            'error': f'Błąd serwera: {str(e)}',
            'issues': [str(e)]
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Sprawdza status serwera"""
    return jsonify({
        'status': 'OK',
        'service': 'EML Renderer',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'capabilities': ['html_render', 'png_render', 'validation']
    })


@app.route('/api/info', methods=['POST'])
def get_eml_info():
    """Zwraca szczegółowe informacje o pliku EML"""
    if 'eml_file' not in request.files:
        return jsonify({'error': 'Brak pliku EML'}), 400

    file = request.files['eml_file']
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400

    try:
        eml_content = file.read()
        processor = EMLProcessor()

        if not processor.load_eml_content(eml_content):
            return jsonify({'error': 'Nie można sparsować pliku EML'}), 400

        is_valid, issues = processor.validate_eml()
        content = processor.extract_content()

        # Szczegółowa analiza
        info = {
            'filename': file.filename,
            'size_bytes': len(eml_content),
            'validation': {
                'is_valid': is_valid,
                'issues': issues
            },
            'headers': content['headers'],
            'structure': {
                'is_multipart': processor.parsed_message.is_multipart(),
                'content_type': processor.parsed_message.get_content_type(),
                'has_html': bool(content['html_body']),
                'has_text': bool(content['text_body']),
                'attachments_count': len(content['attachments'])
            },
            'attachments': content['attachments'],
            'security': {
                'has_spf': 'Received-SPF' in content['headers'],
                'has_dkim': 'DKIM-Signature' in content['headers'],
                'has_auth_results': 'Authentication-Results' in content['headers']
            }
        }

        # Analiza treści
        if content['text_body']:
            info['text_analysis'] = {
                'length': len(content['text_body']),
                'lines': content['text_body'].count('\n') + 1,
                'words': len(content['text_body'].split())
            }

        if content['html_body']:
            info['html_analysis'] = {
                'length': len(content['html_body']),
                'has_scripts': '<script' in content['html_body'].lower(),
                'has_forms': '<form' in content['html_body'].lower(),
                'has_images': '<img' in content['html_body'].lower(),
                'has_links': '<a' in content['html_body'].lower()
            }

        return jsonify(info)

    except Exception as e:
        logger.error(f"Błąd analizy: {e}")
        return jsonify({'error': f'Błąd serwera: {str(e)}'}), 500


if __name__ == '__main__':
    print("🚀 Uruchamianie EML Render Server...")
    print("📡 Dostępne endpointy:")
    print("   GET  /                 - Interfejs web")
    print("   POST /render           - Renderowanie EML")
    print("   POST /api/validate     - Walidacja EML")
    print("   POST /api/info         - Szczegółowe info")
    print("   GET  /api/health       - Status serwera")
    print("🌐 Serwer dostępny na: http://0.0.0.0:5000")

    app.run(host='0.0.0.0', port=5000, debug=False)