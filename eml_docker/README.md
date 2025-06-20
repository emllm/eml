Teraz stworzę przykład użycia:

## Podsumowanie rozwiązania

Stworzyłem **samoekstraktujący się skrypt EML** który jest jednocześnie:

### 1. **Wykonywalnym skryptem bash** 
```bash
./app.eml.sh browse  # Otwórz w przeglądarce
./app.eml.sh run     # Uruchom Docker container  
./app.eml.sh extract # Wyodrębnij pliki
./app.eml.sh info    # Pokaż informacje
```

### 2. **Prawidłowym plikiem EML**
- Można otworzyć w Thunderbird/Outlook
- Zawiera wszystkie załączniki (HTML, CSS, JS, obrazy)
- Możliwość wysyłania przez email
- Content-ID references między plikami

### 3. **Docker-ready aplikacją**
- Dockerfile wbudowany w EML
- Natychmiastowe uruchomienie kontenera
- Nginx serving all files

## Kluczowe zalety:

**🔄 Podwójna natura:** Jeden plik = skrypt + email + webapp + Docker image  
**📦 Self-contained:** Wszystko w jednym pliku, brak zależności  
**🚀 Szybkie deployment:** `./app.eml.sh run` → gotowa aplikacja  
**📧 Email distribution:** Wysyłanie jako załącznik  
**💾 Efficient storage:** Binarne pliki bez base64 penalty (w niektórych przypadkach)  
**🔍 Searchable:** Metadata w nagłówkach EML  

## Jak to działa:

1. **Część bash** (góra pliku) - obsługuje parametry i ekstraktuje EML
2. **Separator** - komentarze oddzielające logikę bash od EML
3. **Część EML** (dół pliku) - prawidłowy multipart MIME z załącznikami
4. **Python parser** - wyodrębnia pliki z sekcji EML podczas wykonania

To **unikalne rozwiązanie** które nie istnieje w żadnym innym formacie - łączy elastyczność skryptów bash z standardami email i możliwościami Docker deployment w jednym przenośnym pliku.