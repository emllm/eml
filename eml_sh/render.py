#!/usr/bin/env python3
"""
Podstawowy renderer plików EML używający wbudowanych bibliotek Python.
Umożliwia parsowanie, walidację i konwersję EML do HTML.
"""

import email
from email.parser import BytesParser
from email import policy
import html
import os
import tempfile
import webbrowser
from pathlib import Path


class EMLRenderer:
    def __init__(self):
        self.parsed_message = None

    def load_eml(self, eml_path):
        """Wczytuje plik EML"""
        try:
            with open(eml_path, 'rb') as fp:
                self.parsed_message = BytesParser(policy=policy.default).parse(fp)
            return True
        except Exception as e:
            print(f"Błąd podczas wczytywania EML: {e}")
            return False

    def validate_structure(self):
        """Sprawdza poprawność struktury EML"""
        if not self.parsed_message:
            return False, "Brak wczytanej wiadomości"

        issues = []

        # Sprawdź podstawowe nagłówki
        required_headers = ['From', 'To', 'Subject', 'Date']
        for header in required_headers:
            if not self.parsed_message.get(header):
                issues.append(f"Brak nagłówka: {header}")

        # Sprawdź defekty
        if self.parsed_message.defects:
            for defect in self.parsed_message.defects:
                issues.append(f"Defekt: {defect}")

        return len(issues) == 0, issues

    def extract_content(self):
        """Wyodrębnia treść wiadomości"""
        if not self.parsed_message:
            return None

        content = {
            'headers': {},
            'text_body': '',
            'html_body': '',
            'attachments': []
        }

        # Wyodrębnij nagłówki
        for key in self.parsed_message.keys():
            content['headers'][key] = self.parsed_message[key]

        # Wyodrębnij treść
        if self.parsed_message.is_multipart():
            for part in self.parsed_message.walk():
                content_type = part.get_content_type()

                if content_type == 'text/plain':
                    content['text_body'] = part.get_content()
                elif content_type == 'text/html':
                    content['html_body'] = part.get_content()
                elif part.get_filename():
                    # Załącznik
                    content['attachments'].append({
                        'filename': part.get_filename(),
                        'content_type': content_type,
                        'size': len(part.get_payload(decode=True) or b'')
                    })
        else:
            # Pojedyncza część
            if self.parsed_message.get_content_type() == 'text/html':
                content['html_body'] = self.parsed_message.get_content()
            else:
                content['text_body'] = self.parsed_message.get_content()

        return content

    def render_to_html(self, output_path=None):
        """Renderuje EML do HTML"""
        content = self.extract_content()
        if not content:
            return None

        # Generuj HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EML Viewer</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        .header-item {{ margin: 5px 0; }}
        .label {{ font-weight: bold; color: #333; }}
        .content {{ background-color: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .attachments {{ margin-top: 20px; }}
        .attachment {{ background-color: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Nagłówki wiadomości</h2>
"""

        for key, value in content['headers'].items():
            escaped_value = html.escape(str(value))
            html_content += f'        <div class="header-item"><span class="label">{key}:</span> {escaped_value}</div>\n'

        html_content += """    </div>

    <div class="content">
        <h3>Treść wiadomości</h3>
"""

        if content['html_body']:
            html_content += f'        <div class="html-body">{content["html_body"]}</div>\n'
        elif content['text_body']:
            escaped_text = html.escape(content['text_body'])
            html_content += f'        <pre class="text-body">{escaped_text}</pre>\n'
        else:
            html_content += '        <p>Brak treści do wyświetlenia</p>\n'

        html_content += "    </div>\n"

        if content['attachments']:
            html_content += """    
    <div class="attachments">
        <h3>Załączniki</h3>
"""
            for att in content['attachments']:
                html_content += f"""        <div class="attachment">
            <strong>{html.escape(att['filename'])}</strong><br>
            Typ: {att['content_type']}, Rozmiar: {att['size']} bajtów
        </div>\n"""
            html_content += "    </div>\n"

        html_content += """
</body>
</html>"""

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return html_content

    def open_in_browser(self):
        """Otwiera renderowaną wiadomość w przeglądarce"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html',
                                         delete=False, encoding='utf-8') as f:
            html_content = self.render_to_html()
            f.write(html_content)
            temp_path = f.name

        webbrowser.open(f'file://{temp_path}')
        return temp_path


# Przykład użycia
if __name__ == "__main__":
    # Utwórz przykładowy plik EML do testów
    # with open('extracted_content/original.eml', 'r') as f:
    #     sample_eml = f.read()
    # Utwórz przykładowy plik EML do testów
    sample_eml = """From: sender@example.com
To: recipient@example.com
Subject: Test Message
Date: Wed, 21 Jun 2025 10:00:00 +0000
Content-Type: text/html; charset=utf-8

<html>
<body>
<h1>Testowa wiadomość</h1>
<p>To jest przykładowa wiadomość HTML w formacie EML.</p>
<p>Zawiera <strong>pogrubiony tekst</strong> i <em>kursywę</em>.</p>
</body>
</html>"""
    # Zapisz przykład do pliku
    with open('sample.eml', 'w') as f:
        f.write(sample_eml)

    # Użyj renderera
    renderer = EMLRenderer()

    if renderer.load_eml('sample.eml'):
        print("✅ Plik EML wczytany pomyślnie")

        # Walidacja
        is_valid, issues = renderer.validate_structure()
        if is_valid:
            print("✅ Struktura EML jest poprawna")
        else:
            print("⚠️ Znalezione problemy:")
            for issue in issues:
                print(f"  - {issue}")

        # Wyodrębnij informacje
        content = renderer.extract_content()
        print(f"\n📧 Informacje o wiadomości:")
        print(f"  - Od: {content['headers'].get('From', 'N/A')}")
        print(f"  - Do: {content['headers'].get('To', 'N/A')}")
        print(f"  - Temat: {content['headers'].get('Subject', 'N/A')}")
        print(f"  - Załączniki: {len(content['attachments'])}")

        # Renderuj do HTML
        html_output = 'rendered_email.html'
        renderer.render_to_html(html_output)
        print(f"✅ Wiadomość wyrenderowana do: {html_output}")

        # Otwórz w przeglądarce
        # temp_file = renderer.open_in_browser()
        # print(f"🌐 Otwarto w przeglądarce: {temp_file}")
    else:
        print("❌ Nie udało się wczytać pliku EML")

    # Posprzątaj
    if os.path.exists('sample.eml'):
        os.remove('sample.eml')