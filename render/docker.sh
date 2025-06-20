#!/bin/bash
# Setup i użycie EMLRender Docker Container
# Źródło: https://github.com/xme/emlrender

echo "🐳 Konfiguracja EMLRender Docker Container"

# 1. Pobierz gotowy obraz z Docker Hub
echo "📥 Pobieranie obrazu emlrender..."
docker pull rootshell/emlrender:latest

# 2. Uruchom kontener
echo "🚀 Uruchamianie kontenera emlrender..."
docker run -d --name emlrender -p 8443:443 rootshell/emlrender:latest

# Poczekaj na uruchomienie
sleep 5

echo "✅ Kontener emlrender działa na porcie 8443"

# 3. Inicjalizacja i tworzenie konta admin
echo "🔐 Inicjalizacja bazy użytkowników..."
curl -k -X POST -d '{"password":"admin123"}' https://localhost:8443/init

echo -e "\n👤 Tworzenie konta użytkownika..."
curl -k -u admin:admin123 -X POST -d '{"username":"user", "password":"user123"}' https://localhost:8443/users/add

echo -e "\n📋 Lista użytkowników:"
curl -k -u admin:admin123 https://localhost:8443/users/list

echo -e "\n"
echo "🎉 EMLRender jest gotowy do użycia!"
echo "🌐 Panel web: https://localhost:8443/upload"
echo "🔑 Login: user / user123"
echo "📚 Pomoc: https://localhost:8443/help"
echo ""
echo "Przykład użycia API:"
echo "curl -k -u user:user123 -F file=@\"twoj_plik.eml\" -o rendered.png https://localhost:8443/upload"