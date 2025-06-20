#!/usr/bin/env python3
"""
Zaawansowany renderer EML używający biblioteki eml-parser.
Instalacja: pip install eml-parser python-magic-bin
"""

import json
import datetime
import eml_parser
import html
from pathlib import Path
import tempfile
import webbrowser


class AdvancedEMLRenderer:
    def __init__(self):
        self.parser = eml_parser.EmlParser()
        self.parsed_data = None

    def json_serial(self, obj):
        """JSON serializer dla obiektów datetime"""
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def load_eml(self, eml_path):
        """Wczytuje i parsuje plik EML"""
        try:
            with open(eml_path, 'rb') as fhdl:
                raw_email = fhdl.read()

            self.parsed_data = self.parser.decode_email_bytes(raw_email)
            return True
        except Exception as e:
            print(f"Błąd podczas parsowania EML: {e}")
            return False

    def validate_email(self):
        """Waliduje strukturę i poprawność emaila"""
        if not self.parsed_data:
            return False, ["Brak danych do walidacji"]

        issues = []
        header = self.parsed_data.get('header', {})

        # Sprawdź wymagane pola
        required_fields = ['from', 'to', 'subject', 'date']
        for field in required_fields:
            if not header.get(field):
                issues.append(f"Brak wymaganego pola: {field}")

        # Sprawdź poprawność adresów email
        from_addr = header.get('from')
        if from_addr and '@' not in str(from_addr):
            issues.append("Niepoprawny format adresu nadawcy")

        to_addrs = header.get('to', [])
        if isinstance(to_addrs, list):
            for addr in to_addrs:
                if '@' not in str(addr):
                    issues.append(f"Niepoprawny format adresu odbiorcy: {addr}")

        # Sprawdź załączniki
        attachments = self.parsed_data.get('attachment', [])
        for i, att in enumerate(attachments):
            if not att.get('filename'):
                issues.append(f"Załącznik {i + 1} nie ma nazwy pliku")
            if not att.get('hash'):
                issues.append(f"Załącznik {i + 1} nie ma hash'a - możliwa korupcja")

        return len(issues) == 0, issues

    def extract_detailed_info(self):
        """Wyodrębnia szczegółowe informacje z emaila"""
        if not self.parsed_data:
            return None

        info = {
            'basic_info': {},
            'technical_details': {},
            'security_info': {},
            'content_info': {},
            'attachments': []
        }

        header = self.parsed_data.get('header', {})

        # Podstawowe informacje
        info['basic_info'] = {
            'from': header.get('from'),
            'to': header.get('to', []),
            'cc': header.get('cc', []),
            'bcc': header.get('bcc', []),
            'subject': header.get('subject'),
            'date': header.get('date'),
            'message_id': header.get('header', {}).get('message-id')
        }

        # Szczegóły techniczne
        info['technical_details'] = {
            'received_chain': header.get('received', []),
            'content_type': header.get('header', {}).get('content-type'),
            'encoding': header.get('header', {}).get('content-transfer-encoding'),
            'mime_version': header.get('header', {}).get('mime-version'),
            'user_agent': header.get('header', {}).get('user-agent')
        }

        # Informacje bezpieczeństwa
        security_headers = header.get('header', {})
        info['security_info'] = {
            'spf': security_headers.get('received-spf'),
            'dkim': security_headers.get('dkim-signature'),
            'authentication_results': security_headers.get('authentication-results')
        }

        # Treść
        body_parts = self.parsed_data.get('body', [])
        info['content_info'] = {
            'parts_count': len(body_parts),
            'has_html': any('text/html' in str(part.get('content_header', {})) for part in body_parts),
            'has_text': any('text/plain' in str(part.get('content_header', {})) for part in body_parts),
            'total_size': sum(len(str(part.get('content', ''))) for part in body_parts)
        }

        # Załączniki
        attachments = self.parsed_data.get('attachment', [])
        for att in attachments:
            info['attachments'].append({
                'filename': att.get('filename'),
                'content_type': att.get('content_type'),
                'size': att.get('size'),
                'hash': att.get('hash'),
                'extension': att.get('extension')
            })

        return info

    def render_to_html(self, output_path=None, include_raw_data=False):
        """Renderuje email do przejrzystego HTML"""
        if not self.parsed_data:
            return None

        info = self.extract_detailed_info()
        is_valid, issues = self.validate_email()

        html_content = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EML Analysis Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .status {{ padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        .status.valid {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .status.invalid {{ background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .field {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #495057; }}
        .value {{ margin-left: 10px; }}
        .issues {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; }}
        .technical {{ font-family: 'Courier New', monospace; font-size: 12px; background-color: #f8f9fa; padding: 10px; border-radius: 3px; }}
        .attachment {{ background-color: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
        h2 {{ color: #343a40; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h3 {{ color: #495057; }}
        .content-preview {{ max-height: 300px; overflow-y: auto; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 Analiza pliku EML</h1>

        <div class="status {'valid' if is_valid else 'invalid'}">
            <strong>Status walidacji: {'✅ Poprawny' if is_valid else '❌ Problemy znalezione'}</strong>
"""

        if not is_valid:
            html_content += "            <ul>\n"
            for issue in issues:
                html_content += f"                <li>{html.escape(issue)}</li>\n"
            html_content += "            </ul>\n"

        html_content += """        </div>

        <div class="grid">
            <div class="card">
                <h2>📄 Podstawowe informacje</h2>
"""

        basic_info = info['basic_info']
        for key, value in basic_info.items():
            if value:
                display_key = key.replace('_', ' ').title()
                if isinstance(value, list):
                    value_str = ', '.join(str(v) for v in value)
                else:
                    value_str = str(value)
                html_content += f'                <div class="field"><span class="label">{display_key}:</span><span class="value">{html.escape(value_str)}</span></div>\n'

        html_content += """            </div>

            <div class="card">
                <h2>🔧 Szczegóły techniczne</h2>
"""

        tech_details = info['technical_details']
        for key, value in tech_details.items():
            if value:
                display_key = key.replace('_', ' ').title()
                if isinstance(value, list):
                    value_str = f"{len(value)} wpisów"
                else:
                    value_str = str(value)
                html_content += f'                <div class="field"><span class="label">{display_key}:</span><span class="value">{html.escape(value_str)}</span></div>\n'

        html_content += """            </div>

            <div class="card">
                <h2>🔒 Bezpieczeństwo</h2>
"""

        security_info = info['security_info']
        for key, value in security_info.items():
            if value:
                display_key = key.replace('_', ' ').title()
                html_content += f'                <div class="field"><span class="label">{display_key}:</span><span class="value">{html.escape(str(value))}</span></div>\n'

        html_content += """            </div>

            <div class="card">
                <h2>📊 Analiza zawartości</h2>
"""

        content_info = info['content_info']
        for key, value in content_info.items():
            display_key = key.replace('_', ' ').title()
            if isinstance(value, bool):
                value_str = "Tak" if value else "Nie"
            else:
                value_str = str(value)
            html_content += f'                <div class="field"><span class="label">{display_key}:</span><span class="value">{value_str}</span></div>\n'

        html_content += """            </div>
        </div>
"""

        # Załączniki
        if info['attachments']:
            html_content += """        
        <div class="card">
            <h2>📎 Załączniki</h2>
"""
            for i, att in enumerate(info['attachments'], 1):
                html_content += f"""            <div class="attachment">
                <strong>#{i}: {html.escape(att.get('filename', 'Nieznana nazwa'))}</strong><br>
                Typ: {att.get('content_type', 'Nieznany')}<br>
                Rozmiar: {att.get('size', 'Nieznany')} bajtów<br>
                Hash: <code>{att.get('hash', 'Brak')[:16]}...</code>
            </div>\n"""
            html_content += "        </div>\n"

        # Treść emaila
        body_parts = self.parsed_data.get('body', [])
        if body_parts:
            html_content += """
        <div class="card">
            <h2>📝 Treść wiadomości</h2>
"""
            for i, part in enumerate(body_parts, 1):
                content = part.get('content', '')
                if content:
                    content_preview = str(content)[:1000] + "..." if len(str(content)) > 1000 else str(content)
                    html_content += f"""            <h3>Część {i}</h3>
            <div class="content-preview">
                <pre>{html.escape(content_preview)}</pre>
            </div>\n"""
            html_content += "        </div>\n"

        # Surowe dane (opcjonalnie)
        if include_raw_data:
            html_content += f"""
        <div class="card">
            <h2>🔍 Surowe dane (JSON)</h2>
            <div class="technical">
                <pre>{html.escape(json.dumps(self.parsed_data, default=self.json_serial, indent=2, ensure_ascii=False))}</pre>
            </div>
        </div>
"""

        html_content += """
    </div>
</body>
</html>"""

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return html_content

    def generate_report(self, output_file='eml_report.html'):
        """Generuje kompletny raport z analizy EML"""
        return self.render_to_html(output_file, include_raw_data=True)


# Przykład użycia
if __name__ == "__main__":
    renderer = AdvancedEMLRenderer()

    # Stwórz przykładowy EML do testów
    sample_eml = """From: test@example.com
To: recipient@example.com
Subject: =?UTF-8?B?VGVzdG93YSB3aWFkb21vxZvEhw==?=
Date: Wed, 21 Jun 2025 10:00:00 +0000
Message-ID: <test123@example.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/html; charset=UTF-8

<html>
<body>
<h1>Test HTML Email</h1>
<p>To jest testowa wiadomość z <strong>HTML</strong>.</p>
</body>
</html>

--boundary123
Content-Type: application/pdf; name="document.pdf"
Content-Disposition: attachment; filename="document.pdf"

JVBERi0xLjQKJcOkw7zDtsO8CjIgMCBvYmoKPDwKL0xlbmd0aCAzIDAgUgo+PgpzdHJlYW0K

--boundary123--
"""

    with open('advanced_sample.eml', 'w') as f:
        f.write(sample_eml)

    if renderer.load_eml('advanced_sample.eml'):
        print("✅ EML wczytany pomyślnie")

        # Walidacja
        is_valid, issues = renderer.validate_email()
        print(f"Walidacja: {'✅ OK' if is_valid else '❌ Problemy'}")
        if issues:
            for issue in issues:
                print(f"  - {issue}")

        # Generuj raport
        report_file = 'detailed_eml_report.html'
        renderer.generate_report(report_file)
        print(f"📊 Szczegółowy raport wygenerowany: {report_file}")

        # Wyświetl podstawowe info
        info = renderer.extract_detailed_info()
        print(f"\n📧 Podsumowanie:")
        print(f"  - Od: {info['basic_info']['from']}")
        print(f"  - Temat: {info['basic_info']['subject']}")
        print(f"  - Załączniki: {len(info['attachments'])}")
        print(f"  - Części treści: {info['content_info']['parts_count']}")

    # Posprzątaj
    import os

    if os.path.exists('advanced_sample.eml'):
        os.remove('advanced_sample.eml')