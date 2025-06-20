#!/usr/bin/env python3
"""
Klient Python do komunikacji z EMLRender Docker API
"""

import requests
import urllib3
import json
import os
from pathlib import Path
import zipfile
import tempfile

# Wyłącz ostrzeżenia SSL dla self-signed certyfikatów
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EMLRenderClient:
    def __init__(self, base_url="https://localhost:8443", username="user", password="user123"):
        self.base_url = base_url
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.verify = False  # Ignoruj SSL dla self-signed cert

    def test_connection(self):
        """Testuje połączenie z serwerem"""
        try:
            response = self.session.get(f"{self.base_url}/help", auth=self.auth)
            return response.status_code == 200
        except Exception as e:
            print(f"Błąd połączenia: {e}")
            return False

    def render_eml_file(self, eml_path, output_path=None, password=None):
        """
        Renderuje plik EML do PNG

        Args:
            eml_path: Ścieżka do pliku EML
            output_path: Ścieżka wyjściowa PNG (opcjonalna)
            password: Hasło do ZIP jeśli plik jest w archiwum
        """
        if not os.path.exists(eml_path):
            raise FileNotFoundError(f"Plik {eml_path} nie istnieje")

        if not output_path:
            output_path = str(Path(eml_path).with_suffix('.png'))

        files = {'file': open(eml_path, 'rb')}
        data = {}

        if password:
            data['password'] = password

        try:
            response = self.session.post(
                f"{self.base_url}/upload",
                files=files,
                data=data,
                auth=self.auth
            )

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True, output_path
            else:
                return False, f"HTTP {response.status_code}: {response.text}"

        except Exception as e:
            return False, str(e)
        finally:
            files['file'].close()

    def render_eml_from_zip(self, zip_path, zip_password, output_path=None):
        """Renderuje EML z archiwum ZIP"""
        return self.render_eml_file(zip_path, output_path, zip_password)

    def batch_render(self, eml_directory, output_directory=None):
        """
        Renderuje wszystkie pliki EML z katalogu

        Args:
            eml_directory: Katalog z plikami EML
            output_directory: Katalog wyjściowy (domyślnie taki sam)
        """
        if not output_directory:
            output_directory = eml_directory

        Path(output_directory).mkdir(exist_ok=True)

        results = []
        eml_files = list(Path(eml_directory).glob("*.eml"))

        print(f"🔄 Renderowanie {len(eml_files)} plików EML...")

        for eml_file in eml_files:
            output_path = Path(output_directory) / f"{eml_file.stem}.png"

            print(f"  📧 {eml_file.name} -> {output_path.name}")
            success, result = self.render_eml_file(str(eml_file), str(output_path))

            results.append({
                'file': eml_file.name,
                'success': success,
                'output': str(output_path) if success else None,
                'error': result if not success else None
            })

        return results


# Przykład użycia i funkcje pomocnicze
def create_sample_eml_files():
    """Tworzy przykładowe pliki EML do testów"""
    samples = {
        'simple.eml': """From: sender@example.com
To: recipient@example.com
Subject: Prosta wiadomość testowa
Date: Wed, 21 Jun 2025 10:00:00 +0000
Content-Type: text/plain; charset=utf-8

To jest prosta wiadomość tekstowa do testowania EMLRender.
Zawiera podstawowe informacje i treść w formacie plain text.
""",
        'html.eml': """From: marketing@example.com
To: customer@example.com
Subject: =?UTF-8?B?V2lhZG9tb8Sbc8SHIEhUTUw=?=
Date: Wed, 21 Jun 2025 11:00:00 +0000
MIME-Version: 1.0
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Newsletter</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
        .content { padding: 20px; }
        .footer { background-color: #f1f1f1; padding: 10px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Witaj w naszym newsletterze!</h1>
    </div>
    <div class="content">
        <h2>Najnowsze wiadomości</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
        <ul>
            <li>Pierwsza wiadomość</li>
            <li>Druga wiadomość</li>
            <li>Trzecia wiadomość</li>
        </ul>
        <a href="#" style="background-color: #008CBA; color: white; padding: 10px 20px; text-decoration: none;">Kliknij tutaj</a>
    </div>
    <div class="footer">
        <p>© 2025 Example Corp. Wszystkie prawa zastrzeżone.</p>
    </div>
</body>
</html>
""",
        'multipart.eml': """From: support@example.com
To: user@example.com
Subject: Wiadomość z załącznikiem
Date: Wed, 21 Jun 2025 12:00:00 +0000
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/html; charset=UTF-8

<html>
<body>
<h2>Wiadomość z załącznikiem</h2>
<p>Ta wiadomość zawiera załącznik w formacie PDF.</p>
<p><strong>Uwaga:</strong> Sprawdź załącznik przed otwarciem!</p>
</body>
</html>

--boundary123
Content-Type: application/pdf; name="dokument.pdf"
Content-Disposition: attachment; filename="dokument.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJcOkw7zDtsO8CjIgMCBvYmoKPDwKL0xlbmd0aCAzIDAgUgo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjcyIDcyMCBUZAooSGVsbG8gV29ybGQhKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCgp4cmVmCjAgMwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTAgMDAwMDAgbiAKMDAwMDAwMDA3OSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDMKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjE3MwolJUVPRg==

--boundary123--
"""
    }

    os.makedirs('sample_emls', exist_ok=True)

    for filename, content in samples.items():
        with open(f'sample_emls/{filename}', 'w', encoding='utf-8') as f:
            f.write(content)

    return list(samples.keys())


def main():
    """Główna funkcja demonstracyjna"""
    print("🚀 EMLRender Python Client - Demo")

    # Inicjalizuj klienta
    client = EMLRenderClient()

    # Testuj połączenie
    print("🔌 Testowanie połączenia z serwerem...")
    if not client.test_connection():
        print("❌ Nie można połączyć się z serwerem EMLRender")
        print("💡 Upewnij się, że kontener Docker działa:")
        print("   docker run -d -p 8443:443 rootshell/emlrender:latest")
        return

    print("✅ Połączenie z serwerem OK")

    # Utwórz przykładowe pliki
    print("\n📁 Tworzenie przykładowych plików EML...")
    sample_files = create_sample_eml_files()
    print(f"✅ Utworzono {len(sample_files)} plików przykładowych")

    # Test renderowania pojedynczego pliku
    print("\n🎨 Test renderowania pojedynczego pliku...")
    success, result = client.render_eml_file('sample_emls/html.eml', 'html_rendered.png')

    if success:
        print(f"✅ Plik wyrenderowany: {result}")
    else:
        print(f"❌ Błąd renderowania: {result}")

    # Test renderowania wsadowego
    print("\n🔄 Test renderowania wsadowego...")
    os.makedirs('rendered_outputs', exist_ok=True)
    results = client.batch_render('sample_emls', 'rendered_outputs')

    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Wyniki renderowania wsadowego:")
    print(f"   ✅ Udane: {successful}/{len(results)}")
    print(f"   ❌ Błędy: {len(results) - successful}/{len(results)}")

    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {result['file']}")
        if not result['success']:
            print(f"      Błąd: {result['error']}")

    print(f"\n🎯 Gotowe! Sprawdź katalog 'rendered_outputs' aby zobaczyć wyniki.")


if __name__ == "__main__":
    main()