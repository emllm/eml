# Własny kontener Docker do renderowania EML
FROM python:3.11-slim

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb \
    libmagic1 \
    libmagic-dev \
    file \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj requirements
COPY requirements.txt .

# Zainstaluj zależności Python
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY eml_render_server.py .
COPY templates/ templates/
COPY static/ static/

# Utwórz katalogi robocze
RUN mkdir -p /app/uploads /app/outputs /app/temp

# Ustaw zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Expose port
EXPOSE 5000

# Utwórz użytkownika non-root
RUN useradd -m -u 1000 emluser && chown -R emluser:emluser /app
USER emluser

# Uruchom aplikację
CMD ["python", "eml_render_server.py"]