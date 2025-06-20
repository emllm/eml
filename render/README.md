# 📧 Kompletny Przewodnik Instalacji - Renderowanie Plików EML

## 🎯 Wprowadzenie

Ten przewodnik opisuje **3 główne rozwiązania** do renderowania i walidacji plików EML:

1. **🐍 Biblioteki Python** - Integracja bezpośrednia
2. **🐳 Docker EMLRender** - Gotowe rozwiązanie  
3. **🔧 Własny serwer Docker** - Pełna kontrola

---

## 📋 Wymagania Systemowe

### Minimalne wymagania:
- **Python 3.8+**
- **Docker 20.0+** (dla rozwiązań Docker)
- **Git** (opcjonalnie)
- **curl** (do testowania API)

### Sprawdzenie wymagań:
```bash
python --version
docker --version
git --version
curl --version
```

---

## 🐍 Rozwiązanie 1: Biblioteki Python

### Instalacja podstawowa (wbudowane biblioteki)

```bash
# Nie wymaga dodatkowych instalacji - używa wbudowanych bibliotek Python
python -c "import email; print('✅ Gotowe!')"
```

**Zastosowanie:** Podstawowe parsowanie i renderowanie EML

### Instalacja zaawansowana (eml-parser)

```bash
# Instalacja biblioteki eml-parser
pip install eml-parser python-magic-bin

# Linux/macOS - dodatkowe zależności
sudo apt-get install libmagic1 libmagic-dev  # Ubuntu/Debian
# lub
brew install libmagic  # macOS

# Weryfikacja
python -c "import eml_parser; print('✅ eml-parser gotowy!')"
```

**Zastosowanie:** Zaawansowana analiza, walidacja bezpieczeństwa

### Przykład użycia:

```python
# Podstawowe użycie
from eml_renderer_basic import EMLRenderer

renderer = EMLRenderer()
renderer.load_eml('twoja_wiadomosc.eml')
renderer.render_to_html('output.html')
renderer.open_in_browser()
```

```python
# Zaawansowane użycie
from eml_advanced_parser import AdvancedEMLRenderer

renderer = AdvancedEMLRenderer()
renderer.load_eml('twoja_wiadomosc.eml')
is_valid, issues = renderer.validate_email()
renderer.generate_report('detailed_report.html')
```

---

## 🐳 Rozwiązanie 2: Docker EMLRender (Gotowe)

### Instalacja Docker

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# macOS
brew install docker docker-compose

# Windows - pobierz Docker Desktop
```

### Setup EMLRender

```bash
# 1. Pobierz obraz
docker pull rootshell/emlrender:latest

# 2. Uruchom kontener
docker run -d --name emlrender -p 8443:443 rootshell/emlrender:latest

# 3. Poczekaj na uruchomienie (5-10 sekund)
sleep 10

# 4. Inicjalizacja (utwórz konto admin)
curl -k -X POST -d '{"password":"admin123"}' https://localhost:8443/init

# 5. Utwórz konto użytkownika
curl -k -u admin:admin123 -X POST -d '{"username":"user", "password":"user123"}' https://localhost:8443/users/add

# 6. Test
curl -k -u user:user123 https://localhost:8443/help
```

### Użycie przez przeglądarkę:
- Otwórz: `https://localhost:8443/upload`
- Login: `user` / hasło: `user123`
- Prześlij plik EML → pobierz PNG

### Użycie przez API:
```bash
# Renderowanie EML do PNG
curl -k -u user:user123 -F file=@"plik.eml" -o rendered.png https://localhost:8443/upload

# Z archiwum ZIP
curl -k -u user:user123 -F file=@"archiwum.zip" -F password=haslo -o rendered.png https://localhost:8443/upload
```

### Użycie z Python:
```python
from python_eml_client import EMLRenderClient

client = EMLRenderClient(username="user", password="user123")
success, output_path = client.render_eml_file('plik.eml', 'wynik.png')

# Renderowanie wsadowe
results = client.batch_render('katalog_eml/', 'katalog_wyjsciowy/')
```

---

## 🔧 Rozwiązanie 3: Własny Serwer Docker

### Przygotowanie plików

1. **Utwórz katalog projektu:**
```bash
mkdir eml-render-server
cd eml-render-server
```

2. **Skopiuj pliki z artefaktów:**
   - `eml_render_server.py`
   - `requirements.txt`
   - `Dockerfile`
   - `docker-compose.yml`

### Budowanie i uruchomienie

```bash
# Opcja A: Docker Compose (zalecane)
docker-compose up --build -d

# Opcja B: Ręczne budowanie
docker build -t my-eml-server .
docker run -d -p 5000:5000 -v $(pwd)/uploads:/app/uploads my-eml-server
```

### Testowanie

```bash
# Test połączenia
curl http://localhost:5000/api/health

# Test walidacji
curl -X POST -F "eml_file=@plik.eml" http://localhost:5000/api/validate

# Test renderowania HTML
curl -X POST -F "eml_file=@plik.eml" -F "output_format=html" http://localhost:5000/render

# Test renderowania PNG
curl -X POST -F "eml_file=@plik.eml" -F "output_format=png" http://localhost:5000/render -o wynik.png
```

### Interfejs webowy:
- Otwórz: `http://localhost:5000`
- Prześlij plik EML przez formularz

---

## 📊 Porównanie Rozwiązań

| Cecha | Python Biblioteki | Docker EMLRender | Własny Serwer |
|-------|------------------|------------------|---------------|
| **Łatwość instalacji** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Kontrola nad kodem** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **Renderowanie PNG** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **API REST** | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Integracja Python** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Produkcyjność** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 Rekomendacje Użycia

### Wybierz **Biblioteki Python** jeśli:
- ✅ Integrujesz z istniejącą aplikacją Python
- ✅ Potrzebujesz pełnej kontroli nad kodem
- ✅ Chcesz uniknąć Docker
- ✅ Wystarczy ci renderowanie HTML

### Wybierz **Docker EMLRender** jeśli:
- ✅ Potrzebujesz szybkiego rozwiązania
- ✅ Renderowanie PNG jest kluczowe
- ✅ Nie potrzebujesz modyfikować kodu
- ✅ Masz doświadczenie z Docker

### Wybierz **Własny Serwer** jeśli:
- ✅ Potrzebujesz API REST
- ✅ Chcesz pełną kontrolę nad funkcjonalnością
- ✅ Planujesz rozbudowę systemu
- ✅ Potrzebujesz custom features

---

## 🔧 Rozwiązywanie Problemów

### Problem: "Docker not found"
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install docker.io

# Dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER
newgrp docker
```

### Problem: "Port already in use"
```bash
# Sprawdź co używa portu
sudo netstat -tlnp | grep :8443
# lub
sudo lsof -i :8443

# Zatrzymaj konfliktujący proces
docker stop $(docker ps -q --filter "publish=8443")
```

### Problem: "SSL certificate errors"
```bash
# Dla EMLRender - używaj -k flag
curl -k https://localhost:8443/help

# Lub dodaj wyjątek w przeglądarce
```

### Problem: "eml-parser installation failed"
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libmagic1 libmagic-dev

# macOS
brew install libmagic

# Windows
pip install python-magic-bin
```

### Problem: "Permission denied"
```bash
# Upewnij się że pliki mają odpowiednie uprawnienia
chmod +x docker_eml_setup.sh
chmod 644 *.eml

# Dla Docker
sudo chown -R $USER:$USER uploads/ outputs/
```

---

## 📚 Dodatkowe Zasoby

### Dokumentacja:
- [Python email package](https://docs.python.org/3/library/email.html)
- [EMLRender GitHub](https://github.com/xme/emlrender)
- [Docker Documentation](https://docs.docker.com/)

### Przydatne komendy:

```bash
# Sprawdź logi Docker
docker logs emlrender

# Restart kontenera
docker restart emlrender

# Backup danych EMLRender
docker exec emlrender tar czf - /data | gzip > emlrender_backup.tar.gz

# Monitoring zasobów
docker stats emlrender
```

### Przykładowe pliki EML do testów:
- Uruchom `comprehensive_eml_example.py` aby wygenerować pliki testowe
- Lub użyj własnych plików .eml z programów pocztowych

---

## 🎉 Podsumowanie

Po instalacji jednego z rozwiązań będziesz mógł:

1. **📧 Wczytywać pliki EML** z różnych źródeł
2. **🔍 Walidować strukturę** wiadomości email
3. **🎨 Renderować do HTML/PNG** z zachowaniem formatowania
4. **📊 Analizować załączniki** i metadane
5. **🔒 Sprawdzać bezpieczeństwo** (SPF, DKIM, itp.)
6. **⚡ Przetwarzać wsadowo** wiele plików

Wybierz rozwiązanie odpowiednie dla Twoich potrzeb i ciesz się wydajnym renderowaniem plików EML! 🚀