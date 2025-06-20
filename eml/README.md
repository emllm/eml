# Self-Extracting EML Script

This directory contains a self-extracting EML script that combines an email message with an embedded web application.

## Plik `testapp.eml.sh`

### Opis
`testapp.eml.sh` to samorozpakowujący się skrypt, który łączy wiadomość e-mail z osadzoną aplikacją internetową. Plik jest jednocześnie:
1. Wykonywalnym skryptem bash
2. Płynym plikiem EML z załącznikami

### Jak to działa
1. Skrypt zaczyna się od standardowego shebanga `#!/bin/bash`
2. Zawiera dane wiadomości e-mail (nagłówki MIME i zawartość)
3. Dane są oddzielone od kodu skryptu za pomocą znaczników
4. Po uruchomieniu skrypt sam się analizuje i wyodrębnia zawartość

### Użycie
```bash
# Nadaj uprawnienia do wykonania (jeśli potrzebne)
chmod +x testapp.eml.sh

# Uruchomienie z opcjami:
./testapp.eml.sh [polecenie]

Dostępne polecenia:
- extract - Wyodrębnij zawartość
- run     - Uruchom aplikację
- browse  - Otwórz w przeglądarce
- info    - Pokaż informacje o skrypcie
```

### Przykłady
```bash
# Wyodrębnij zawartość do katalogu
./testapp.eml.sh extract

# Uruchom aplikację
./testapp.eml.sh run

# Wyświetl informacje
./testapp.eml.sh info
```

### Wymagania
- Bash
- Standardowe narzędzia systemu Linux (grep, sed, awk, itp.)
- Domyślna przeglądarka internetowa (dla opcji browse)

### Struktura
Po wyodrębnieniu, skrypt tworzy następującą strukturę:
```
/
├── index.html      # Główny plik HTML aplikacji
├── style.css       # Arkusz stylów
└── invoices/       # Katalog z fakturami (jeśli są załączone)
```

### Uwagi
- Skrypt jest samowystarczalny i nie wymaga instalacji dodatkowych zależności
- Wszystkie zasoby są osadzone w pliku skryptu
- Można go bezpiecznie przesyłać jako załącznik e-mail

### Licencja
[Proszę określić licencję, np. MIT, GPL, itp.]
