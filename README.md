# EMLLM - Email-based LLM Application Distribution System

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Apache Camel](https://img.shields.io/badge/Apache%20Camel-3.20.3-FF6D00?logo=apache&logoColor=white)](https://camel.apache.org/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?logo=react&logoColor=white)](https://reactjs.org/)

EMLLM is a complete system that enables the generation and distribution of applications via email using Large Language Models (LLMs). The system allows users to request application generation via email, processes these requests using an LLM, and automatically deploys the generated applications.

## ✨ Features

- **Email-based Application Generation**: Request applications via email and receive generated applications as email attachments
- **LLM Integration**: Process application generation requests using Large Language Models (Mistral 7B via Ollama)
- **Automated Deployment**: Automatically deploy applications upon receipt
- **Web Dashboard**: Monitor requests and deployments through a modern web interface
- **Containerized**: All components run in Docker containers for easy deployment
- **Asynchronous Processing**: Non-blocking architecture for handling multiple requests
- **Extensible**: Easily add support for new application types and deployment targets
- **Self-documenting**: Includes API documentation and usage examples

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 8GB of RAM (16GB recommended for LLM processing)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/emllm/eml.git
   cd eml
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Access the web interface at [http://localhost:3000](http://localhost:3000)

### How It Works

1. **Bot Generator**: Sends random application generation requests via email
2. **Camel Server**: Processes incoming emails, generates applications using LLM, and sends responses
3. **Client Agent**: Monitors for new application emails and deploys them automatically
4. **Web UI**: Provides a dashboard to monitor requests and deployments

### Sending a Request

1. Send an email to `llm@example.com` with your application requirements in the body
2. The system will process your request and send back an email with the generated application
3. The client agent will automatically deploy the application

### Monitoring

- **MailHog Web UI**: [http://localhost:8025](http://localhost:8025) - View sent and received emails
- **Web Dashboard**: [http://localhost:3000](http://localhost:3000) - Monitor requests and deployments

## 🏗️ Project Structure

```
eml/
├── bot-generator/           # Service that sends random application requests
│   ├── Dockerfile
│   └── bot.groovy
├── camel-server/             # Main processing service with Apache Camel
│   ├── build.gradle
│   ├── Dockerfile
│   └── src/
│       └── main/groovy/com/emllm/
│           ├── Application.groovy
│           └── EmailProcessingRoute.groovy
├── client-agent/             # Client agent for deploying applications
│   ├── Dockerfile
│   └── client.groovy
├── web-ui/                   # React-based web dashboard
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.js
│       ├── App.css
│       ├── index.js
│       └── index.css
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

## ⚙️ Configuration

The system is configured using environment variables. Create a `.env` file in the project root with the following variables:

```env
# Mail Server Configuration
SMTP_HOST=mailhog
SMTP_PORT=1025
IMAP_HOST=mailhog
IMAP_PORT=1143

# Email Accounts
BOT_EMAIL=bot@example.com
LLM_EMAIL=llm@example.com
CLIENT_EMAIL=client@example.com
EMAIL_PASSWORD=password

# LLM Configuration
OLLAMA_BASE_URL=http://ollama:11434

# Deployment
DEPLOYMENT_DIR=/app/deployments
```

## 🚀 Running the System

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **View the web dashboard**:
   Open [http://localhost:3000](http://localhost:3000) in your browser

3. **View emails in MailHog**:
   Open [http://localhost:8025](http://localhost:8025) to see all sent and received emails

4. **Stop all services**:
   ```bash
   docker-compose down
   ```

## 🔍 Monitoring and Logs

View logs for a specific service:
```bash
docker-compose logs -f service_name  # e.g., camel-server, client-agent, etc.
```

## 🤖 Available Services

| Service | Description | Port |
|---------|-------------|------|
| mailhog | Email server for development | 8025 (Web UI), 1025 (SMTP), 1143 (IMAP) |
| bot-generator | Sends random application requests | - |
| camel-server | Processes emails and generates applications | 8080 |
| client-agent | Deploys received applications | - |
| ollama | Local LLM server | 11434 |
| web-ui | Web dashboard | 3000 |

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📫 Contact

For questions or support, please open an issue on our [GitHub repository](https://github.com/emllm/eml/issues).

## 📚 Documentation

For more detailed information, please refer to:
- [Installation Guide](docs/installation/index.md)
- [Usage Examples](docs/usage/index.md)
- [API Reference](docs/api/index.md)

---

<p align="center">
  Made with ❤️ by the EMLLM Team
</p>

## About EMLLM

EMLLM is an advanced system for AI-generated software distribution, using email infrastructure as a transport protocol. The system combines the capabilities of Large Language Models with traditional email infrastructure, enabling the automatic distribution of dynamically generated code/applications.

## 📦 Installation

```bash
# Using pip
pip install emllm

# Or using the repository
git clone https://github.com/emllm/eml.git
cd eml
docker-compose up -d
```

## Known Limitations

### Security Considerations
- Code signing and verification challenges
- Email interception vulnerabilities
- Risk of malicious code execution
- Lack of sandboxing mechanisms
- Difficulty in verifying application source

### Scalability
- Email attachment size limits (typically 25-50MB)
- SMTP delivery delays and retry mechanisms
- Lack of real-time deployment status feedback

### Debugging Complexity
- Challenges in debugging distributed email systems
- Lack of standardized E2E monitoring tools
- Difficulties in tracing issues across email hops

### System Integration
- Need for integration with enterprise systems (SSO, Active Directory)
- Limited support for some authentication protocols
- Challenges in corporate email filtering and security policies

### Version Management
- Difficulty in versioning email-distributed applications
- Lack of automatic update mechanisms
- Version conflicts in distributed environments

### Performance
- Performance limitations with large applications
- Long generation and transmission times for large attachments
- Resource constraints on email servers

### User Experience
- Limited interaction capabilities via email
- Lack of standardized email interface design
- Inconsistent rendering across email clients

### Accessibility
- Varying accessibility support across email clients
- Limited screen reader support in generated applications
- Challenges with responsive design in email clients

## System Architecture

```bash
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Request  │───▶│   LLM Generator │───▶│  SMTP Gateway   │
│  (Webhook/API)  │    │   (Code Gen)    │    │   (Email Send)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Metadata      │    │   User Inbox    │
                       │   Packaging     │    │   (Receive)     │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  EML Creation   │    │  Auto Extract   │
                       │  (Self-Extract) │    │   (Execute)     │
                       └─────────────────┘    └─────────────────┘
```

### **Flow procesu:**

1. **Request initiation**: Webhook lub API call z parametrami aplikacji
2. **LLM Processing**: AI generuje kod bazując na input parameters
3. **Metadata enrichment**: Automatyczne dodawanie dependencies, configs
4. **EML Packaging**: Tworzenie samorozpakowującego się email archive
5. **SMTP Delivery**: Wysyłka przez konfigurowany SMTP server
6. **Client Reception**: Otrzymanie i automatyczne przetworzenie
7. **Execution**: Uruchomienie aplikacji w target environment

### **Wykorzystanie webhooków:**

**Inbound webhooks** (triggering generacji):
```json
{
  "app_type": "dashboard",
  "requirements": ["Python", "FastAPI", "Docker"],
  "recipient": "developer@company.com",
  "parameters": {
    "database": "PostgreSQL",
    "auth": "OAuth2",
    "deployment": "containerized"
  }
}
```

**Outbound webhooks** (status notifications):
```json
{
  "status": "email_sent",
  "request_id": "req_12345",
  "recipient": "developer@company.com",
  "timestamp": "2025-06-19T10:30:00Z",
  "tracking_id": "email_67890"
}
```

## Przykłady zastosowań

### **1. Enterprise Internal Tools**
- Automatyczne generowanie admin dashboards
- Custom reporting applications
- One-off automation scripts dla specific tasks

### **2. Client Deliverables**
- Personalized demos dla sales presentations
- Custom integrations dla client environments
- Proof-of-concept applications

### **3. Emergency Deployments**
- Hotfix distribution gdy CI/CD is down
- Disaster recovery tools
- Quick patches dla critical systems

### **4. Training i Development**
- Personalized learning environments
- Custom exercise generators
- Development environment setup

## Techniczne aspekty implementacji

### **LLM Integration considerations:**

**Model selection criteria:**
- Code generation capabilities (Python, JavaScript, Docker)
- Support for structured output (JSON metadata)
- Rate limiting i cost considerations
- Local vs. cloud deployment options

**Prompt engineering patterns:**
```python
GENERATION_PROMPT = """
Generate a complete {app_type} application with the following requirements:
- Technology stack: {tech_stack}
- Deployment target: {deployment_target}
- Features: {features}

Include:
1. Complete source code
2. Dockerfile dla containerization
3. Deployment instructions
4. Configuration files
5. Basic tests

Output as JSON with file paths and contents.
"""
```

### **SMTP Server considerations:**

**Authentication i security:**
- OAuth2 dla Gmail/Office365 integration
- SMTP-AUTH dla dedicated servers
- TLS encryption dla all communications
- Rate limiting dla abuse prevention

**Delivery optimization:**
- Queue management dla bulk operations
- Retry logic dla failed deliveries
- Monitoring i alerting dla SMTP health
- Load balancing across multiple SMTP servers

### **Email formatting strategies:**

**MIME structure optimization:**
```
multipart/mixed
├── text/plain (human readable summary)
├── text/html (rich formatted instructions)
├── application/octet-stream (source_code.zip)
├── application/json (metadata.json)
└── text/x-dockerfile (Dockerfile)
```

**Metadata standardization:**
```json
{
  "version": "1.0",
  "generated_at": "2025-06-19T10:30:00Z",
  "llm_model": "gpt-4",
  "request_id": "req_12345",
  "app_metadata": {
    "name": "Custom Dashboard",
    "type": "web_application",
    "runtime": "python:3.11",
    "dependencies": ["fastapi", "uvicorn", "pydantic"]
  },
  "deployment": {
    "method": "docker",
    "port": 8080,
    "environment_vars": ["DATABASE_URL", "SECRET_KEY"]
  },
  "execution_instructions": [
    "docker build -t custom-dashboard .",
    "docker run -p 8080:8080 custom-dashboard"
  ]
}
```

## Porównanie z alternatywnymi rozwiązaniami

| Aspekt | Email Distribution | GitHub Actions | Docker Registry | Package Managers |
|--------|-------------------|----------------|-----------------|------------------|
| **Setup Complexity** | Niski | Średni | Średni | Wysoki |
| **Infrastructure Deps** | Email only | Git + CI/CD | Registry server | Package repos |
| **Real-time Feedback** | Ograniczony | Excellent | Good | Good |
| **Security** | Podstawowy | Strong | Strong | Excellent |
| **Versioning** | Email history | Git-based | Tag-based | Semantic versioning |
| **Rollback** | Manual resend | Automated | Tag switching | Version downgrade |
| **Enterprise Integration** | Native | Good | Good | Excellent |
| **Debugging** | Limited | Excellent | Good | Good |

## Implementacja referencyjna

System składa się z trzech głównych komponentów:

### **1. AI Code Generator Service**
- REST API dla request handling
- LLM integration (OpenAI/Anthropic/Local)
- Template management system
- Code validation i testing

### **2. Email Distribution Service**  
- SMTP server integration
- Email template generation
- Attachment handling
- Delivery tracking

### **3. Client Integration Tools**
- Email parsing utilities
- Automatic extraction scripts
- Execution wrappers
- Status reporting hooks

## Wnioski i rekomendacje

**Email-based AI software distribution** to interesująca koncepcja dla specific use cases, ale nie zastąpi tradycyjnych methods dla production systems. 

**Zalecane zastosowania:**
- Prototyping i rapid development
- Internal tool distribution w małych teams
- Emergency deployment scenarios
- Educational i training environments

**Nie zalecane dla:**
- Production deployment systems
- Security-critical applications
- High-frequency update cycles
- Applications wymagające complex dependency management

**Kluczowe success factors:**
- Strong email infrastructure
- Proper security protocols
- Clear governance policies
- Comprehensive monitoring
- User education i training



# Uniwersalne launchery dla różnych platform

## 📁 Struktura projektu

```
emllm/
├── src/
│   └── emllm/
│       ├── __init__.py
│       ├── api.py
│       ├── core.py
│       ├── cli.py
│       └── validator.py
├── tests/
├── pyproject.toml
├── Makefile
└── README.md
```

```
universal-webapp/
├── testapp.eml.py          # Główny uniwersalny plik
├── run-windows.bat             # Windows batch launcher  
├── run-macos.command           # macOS double-click launcher
├── run-linux.sh               # Linux shell launcher
├── install-python.md          # Instrukcje instalacji Python
└── README.md                   # Instrukcje użytkowania
```

## 🪟 Windows Batch Launcher (run-windows.bat)

```batch
@echo off
REM Windows Launcher for Universal EML WebApp
REM Automatycznie znajduje Python i uruchamia aplikację

title Universal EML WebApp - Windows

echo.
echo ==========================================
echo    Universal EML WebApp - Windows
echo ==========================================
echo.

REM Sprawdź czy istnieje plik główny
if not exist "testapp.eml.py" (
    echo BLAD: Nie znaleziono pliku testapp.eml.py
    echo Upewnij sie, ze plik znajduje sie w tym samym katalogu.
    pause
    exit /b 1
)

REM Znajdź Python (sprawdź różne możliwe lokalizacje)
set PYTHON_CMD=

REM Sprawdź python3
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

REM Sprawdź python
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :python_found
)

REM Sprawdź py launcher (Windows 10+)
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :python_found
)

REM Sprawdź ścieżki bezpośrednie
if exist "C:\Python3*\python.exe" (
    for /f %%i in ('dir /b "C:\Python3*"') do (
        set PYTHON_CMD="C:\%%i\python.exe"
        goto :python_found
    )
)

REM Python nie znaleziony
echo BLAD: Python nie jest zainstalowany lub nie znajduje sie w PATH
echo.
echo Aby zainstalowac Python:
echo 1. Idz na https://python.org/downloads
echo 2. Pobierz Python 3.8+ dla Windows
echo 3. Podczas instalacji zaznacz "Add Python to PATH"
echo 4. Uruchom ponownie ten plik
echo.
pause
exit /b 1

:python_found
echo Znaleziono Python: %PYTHON_CMD%

REM Sprawdź wersję Python
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Wersja Python: %PYTHON_VERSION%
echo.

REM Pokaż menu wyboru
echo Wybierz akcje:
echo [1] Otworz w przegladarce (domyslnie)
echo [2] Uruchom w Docker
echo [3] Wyodrebnij pliki
echo [4] Pokaz informacje
echo [5] Pomoc
echo.
set /p choice="Wybor (1-5) lub Enter dla domyslnej akcji: "

if "%choice%"=="" set choice=1
if "%choice%"=="1" set ACTION=browse
if "%choice%"=="2" set ACTION=run
if "%choice%"=="3" set ACTION=extract
if "%choice%"=="4" set ACTION=info
if "%choice%"=="5" set ACTION=help

if not defined ACTION (
    echo Nieprawidlowy wybor: %choice%
    pause
    exit /b 1
)

echo.
echo Uruchamianie: %PYTHON_CMD% testapp.eml.py %ACTION%
echo.

REM Uruchom aplikację
%PYTHON_CMD% testapp.eml.py %ACTION%

if %errorlevel% neq 0 (
    echo.
    echo Wystapil blad podczas uruchamiania aplikacji.
    echo Kod bledu: %errorlevel%
)

echo.
echo Nacisnij dowolny klawisz aby zakonczyc...
pause >nul
```

## 🍎 macOS Command Launcher (run-macos.command)

```bash
#!/bin/bash
#
# macOS Launcher for Universal EML WebApp
# Double-click to run, or use from Terminal
#

# macOS specific setup
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

# Change to script directory
cd "$(dirname "$0")"

echo "🍎 Universal EML WebApp - macOS Launcher"
echo "========================================"
echo

# Check if main file exists
if [ ! -f "testapp.eml.py" ]; then
    echo "❌ Błąd: Nie znaleziono pliku testapp.eml.py"
    echo "Upewnij się, że plik znajduje się w tym samym katalogu."
    
    # Show in Finder
    osascript -e 'tell application "Finder" to reveal POSIX file "'$(pwd)'"' 2>/dev/null
    
    echo "Naciśnij Enter aby zamknąć..."
    read
    exit 1
fi

# Find Python
PYTHON_CMD=""

# Check python3 first (preferred on macOS)
if command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python > /dev/null 2>&1; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
    fi
fi

# Check Homebrew Python
if [ -z "$PYTHON_CMD" ] && [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON_CMD="/opt/homebrew/bin/python3"
elif [ -z "$PYTHON_CMD" ] && [ -x "/usr/local/bin/python3" ]; then
    PYTHON_CMD="/usr/local/bin/python3"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Błąd: Python 3 nie jest zainstalowany"
    echo
    echo "Aby zainstalować Python na macOS:"
    echo "1. Zainstaluj Homebrew: https://brew.sh"
    echo "2. Uruchom: brew install python3"
    echo "3. Lub pobierz z: https://python.org/downloads"
    echo
    
    # Offer to open installation page
    osascript -e 'display dialog "Python nie jest zainstalowany. Otworzyć stronę instalacji?" buttons {"Nie", "Tak"} default button "Tak"' 2>/dev/null
    if [ $? -eq 0 ]; then
        open "https://python.org/downloads/macos/"
    fi
    
    echo "Naciśnij Enter aby zamknąć..."
    read
    exit 1
fi

echo "✅ Znaleziono Python: $PYTHON_CMD"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "📍 Wersja: $PYTHON_VERSION"
echo

# Show action menu with macOS styling
if [ "$TERM_PROGRAM" = "" ]; then
    # GUI mode (double-clicked)
    ACTION=$(osascript -e 'choose from list {"browse", "run", "extract", "info", "help"} with prompt "Wybierz akcję:" default items {"browse"}' 2>/dev/null)
    
    if [ "$ACTION" = "false" ]; then
        echo "Anulowano przez użytkownika"
        exit 0
    fi
else
    # Terminal mode
    echo "Wybierz akcję:"
    echo "1) 🌐 browse  - Otwórz w przeglądarce (domyślnie)"
    echo "2) 🐳 run     - Uruchom w Docker"  
    echo "3) 📁 extract - Wyodrębnij pliki"
    echo "4) ℹ️  info    - Pokaż informacje"
    echo "5) ❓ help    - Pomoc"
    echo
    read -p "Wybór (1-5) lub Enter dla domyślnej akcji: " choice
    
    case $choice in
        1|"") ACTION="browse" ;;
        2) ACTION="run" ;;
        3) ACTION="extract" ;;
        4) ACTION="info" ;;
        5) ACTION="help" ;;
        *) 
            echo "❌ Nieprawidłowy wybór: $choice"
            echo "Naciśnij Enter aby zamknąć..."
            read
            exit 1
            ;;
    esac
fi

echo "🚀 Uruchamianie: $PYTHON_CMD testapp.eml.py $ACTION"
echo

# Run the application
$PYTHON_CMD testapp.eml.py $ACTION

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "❌ Wystąpił błąd podczas uruchamiania aplikacji."
    
    # Show error dialog in GUI mode
    if [ "$TERM_PROGRAM" = "" ]; then
        osascript -e 'display dialog "Wystąpił błąd podczas uruchamiania aplikacji. Sprawdź Terminal aby zobaczyć szczegóły." buttons {"OK"} default button "OK"' 2>/dev/null
    fi
fi

# Keep terminal open if launched from Finder
if [ "$TERM_PROGRAM" = "" ]; then
    echo
    echo "Naciśnij Enter aby zamknąć..."
    read
fi
```

## 🐧 Linux Shell Launcher (run-linux.sh)

```bash
#!/bin/bash
#
# Linux Launcher for Universal EML WebApp
# Works on Ubuntu, Debian, Fedora, CentOS, Arch, etc.
#

echo "🐧 Universal EML WebApp - Linux Launcher"
echo "========================================"
echo

# Change to script directory
cd "$(dirname "$0")"

# Check if main file exists
if [ ! -f "testapp.eml.py" ]; then
    echo "❌ Błąd: Nie znaleziono pliku testapp.eml.py"
    echo "Upewnij się, że plik znajduje się w tym samym katalogu."
    exit 1
fi

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$NAME
else
    DISTRO="Unknown Linux"
fi

echo "🖥️  System: $DISTRO"

# Find Python
PYTHON_CMD=""

# Check python3 first (standard on modern Linux)
if command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python > /dev/null 2>&1; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
    fi
fi

# Try alternative locations
if [ -z "$PYTHON_CMD" ]; then
    for py_path in /usr/bin/python3 /usr/local/bin/python3 /opt/python3/bin/python3; do
        if [ -x "$py_path" ]; then
            PYTHON_CMD="$py_path"
            break
        fi
    done
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Błąd: Python 3 nie jest zainstalowany"
    echo
    echo "Aby zainstalować Python 3:"
    
    # Distribution-specific install commands
    if command -v apt > /dev/null 2>&1; then
        echo "Ubuntu/Debian: sudo apt update && sudo apt install python3"
    elif command -v yum > /dev/null 2>&1; then
        echo "CentOS/RHEL:   sudo yum install python3"
    elif command -v dnf > /dev/null 2>&1; then
        echo "Fedora:        sudo dnf install python3"
    elif command -v pacman > /dev/null 2>&1; then
        echo "Arch Linux:    sudo pacman -S python"
    elif command -v zypper > /dev/null 2>&1; then
        echo "openSUSE:      sudo zypper install python3"
    else
        echo "Użyj menedżera pakietów twojej dystrybucji lub pobierz z python.org"
    fi
    
    exit 1
fi

echo "✅ Znaleziono Python: $PYTHON_CMD"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "📍 Wersja: $PYTHON_VERSION"

# Check for Docker (optional)
if command -v docker > /dev/null 2>&1; then
    echo "🐳 Docker: Dostępny"
else
    echo "🐳 Docker: Niedostępny (opcjonalny - potrzebny tylko dla komendy 'run')"
fi

echo

# Show menu
echo "Wybierz akcję:"
echo "1) 🌐 browse  - Otwórz w przeglądarce (domyślnie)"
echo "2) 🐳 run     - Uruchom w Docker"
echo "3) 📁 extract - Wyodrębnij pliki"  
echo "4) ℹ️  info    - Pokaż informacje"
echo "5) ❓ help    - Pomoc"
echo

read -p "Wybór (1-5) lub Enter dla domyślnej akcji: " choice

case $choice in
    1|"") ACTION="browse" ;;
    2) ACTION="run" ;;
    3) ACTION="extract" ;;
    4) ACTION="info" ;;
    5) ACTION="help" ;;
    *) 
        echo "❌ Nieprawidłowy wybór: $choice"
        exit 1
        ;;
esac

echo
echo "🚀 Uruchamianie: $PYTHON_CMD testapp.eml.py $ACTION"
echo

# Run the application
$PYTHON_CMD testapp.eml.py $ACTION

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "❌ Wystąpił błąd podczas uruchamiania aplikacji."
    exit 1
fi

echo
echo "✅ Zakończono pomyślnie"
```

## 📋 Instrukcje instalacji Python (install-python.md)

```markdown
# Instalacja Python dla Universal EML WebApp

## 🪟 Windows

### Opcja 1: Ze strony Python.org (Zalecane)
1. Idź na https://python.org/downloads
2. Pobierz najnowszą wersję Python 3.8+
3. **WAŻNE**: Podczas instalacji zaznacz "Add Python to PATH"
4. Kliknij "Install Now"
5. Po instalacji uruchom `run-windows.bat`

### Opcja 2: Microsoft Store
1. Otwórz Microsoft Store
2. Wyszukaj "Python 3.11" (lub nowszy)
3. Kliknij "Pobierz"
4. Python będzie dostępny jako `python3`

### Opcja 3: Chocolatey
```powershell
choco install python3
```

## 🍎 macOS  

### Opcja 1: Homebrew (Zalecane)
```bash
# Zainstaluj Homebrew jeśli nie masz
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Zainstaluj Python
brew install python3
```

### Opcja 2: Ze strony Python.org
1. Idź na https://python.org/downloads/macos
2. Pobierz installer dla macOS
3. Uruchom installer i podążaj za instrukcjami
4. Python będzie dostępny jako `python3`

### Opcja 3: pyenv (dla zaawansowanych)
```bash
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

## 🐧 Linux

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Fedora
```bash
sudo dnf install python3 python3-pip
```

### CentOS/RHEL 8+
```bash
sudo dnf install python3 python3-pip
```

### CentOS/RHEL 7
```bash
sudo yum install python3 python3-pip
```

### Arch Linux
```bash
sudo pacman -S python python-pip
```

### openSUSE
```bash
sudo zypper install python3 python3-pip
```

## ✅ Weryfikacja instalacji

Po instalacji otwórz terminal/wiersz poleceń i sprawdź:

```bash
python3 --version
# lub
python --version
```

Powinieneś zobaczyć coś jak: `Python 3.8.10` lub nowszy.

## 🐳 Docker (Opcjonalny)

Jeśli chcesz używać komendy `run` (uruchomienie w kontenerze):

### Windows/macOS
1. Pobierz Docker Desktop: https://docker.com/products/docker-desktop
2. Zainstaluj i uruchom
3. Docker będzie dostępny z wiersza poleceń

### Linux
```bash
# Ubuntu/Debian
sudo apt install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER

# Fedora
sudo dnf install docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Arch
sudo pacman -S docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

## 🔧 Rozwiązywanie problemów

### "python nie jest rozpoznany jako polecenie"
- Windows: Reinstaluj Python z opcją "Add to PATH"
- Użyj pełnej ścieżki: `C:\Python311\python.exe`

### "Permission denied" na Linux/macOS
```bash
chmod +x testapp.eml.py
chmod +x run-linux.sh      # Linux
chmod +x run-macos.command # macOS
```

### Python 2 zamiast Python 3
```bash
# Użyj explicit python3
python3 testapp.eml.py browse
```

### Brak uprawnień Docker na Linux
```bash
sudo usermod -aG docker $USER
# Wyloguj się i zaloguj ponownie
```
```

## 📖 README.md - Główne instrukcje

```markdown
# 🌍 Universal EML WebApp - Faktury Maj 2025

**Uniwersalna aplikacja webowa w formacie EML - działa na Windows, macOS i Linux!**

## 🚀 Szybki start

### Automatyczne uruchomienie (Zalecane)

**Windows:**
```
Kliknij dwukrotnie: run-windows.bat
```

**macOS:**
```
Kliknij dwukrotnie: run-macos.command
```

**Linux:**
```bash
./run-linux.sh
```

### Ręczne uruchomienie

```bash
# Wszystkie platformy
python3 testapp.eml.py [komenda]

# Windows (alternatywnie)
python testapp.eml.py [komenda]
```

## 📋 Dostępne komendy

| Komenda | Opis | Przykład |
|---------|------|----------|
| `browse` | Otwórz w przeglądarce (domyślnie) | `python3 testapp.eml.py browse` |
| `run` | Uruchom w Docker na porcie 8080 | `python3 testapp.eml.py run` |
| `extract` | Wyodrębnij pliki do katalogu temp | `python3 testapp.eml.py extract` |
| `info` | Pokaż informacje o pliku | `python3 testapp.eml.py info` |
| `help` | Wyświetl pomoc | `python3 testapp.eml.py help` |

## 🛠️ Instalacja

### Z PyPI

```bash
pip install emllm
```

### Z źródeł

```bash
git clone https://github.com/emllm/eml.git
cd eml
poetry install
```

## 💻 Wymagania systemowe

- **Python 3.8+** (standardowo dostępny)
- **Docker** (opcjonalnie, tylko dla komendy `run`)
- **Przeglądarka** (dowolna nowoczesna)

## 🎯 Funkcje

✅ **Uniwersalność** - jeden plik działa wszędzie  
✅ **Samorozpakowywanie** - wszystko w jednym pliku  
✅ **Kompatybilność email** - prawidłowy format EML  
✅ **Docker ready** - natywne wsparcie kontenerów  
✅ **Responsive design** - działa na wszystkich urządzeniach  
✅ **Zero instalacji** - tylko Python (już zainstalowany)  

## 🔧 Instalacja Python

Jeśli Python nie jest zainstalowany, zobacz: [install-python.md](install-python.md)

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📧 Format EML

Ten plik jest **jednocześnie**:
- Wykonywalnym skryptem Python
- Prawidłowym emailem EML
- Kompletną aplikacją webową

Możesz go:
- Uruchomić jako skrypt
- Otworzyć w kliencie email (Outlook, Thunderbird)
- Wysłać przez email jako załącznik

## 🌐 Wsparcie platform

| Platform | Status | Launcher | Python |
|----------|--------|----------|--------|
| Windows 10/11 | ✅ | `run-windows.bat` | `python3` / `python` |
| macOS 10.15+ | ✅ | `run-macos.command` | `python3` |
| Ubuntu 18.04+ | ✅ | `run-linux.sh` | `python3` |
| Debian 10+ | ✅ | `run-linux.sh` | `python3` |
| Fedora 30+ | ✅ | `run-linux.sh` | `python3` |
| CentOS 8+ | ✅ | `run-linux.sh` | `python3` |
| Arch Linux | ✅ | `run-linux.sh` | `python3` |

## 🐳 Docker

Jeśli masz Docker, możesz uruchomić aplikację w kontenerze:

```bash
python3 testapp.eml.py run
```

Aplikacja będzie dostępna na: http://localhost:8080

## 📱 Mobile

Aplikacja działa również w przeglądarkach mobilnych:
- Safari (iOS)
- Chrome (Android)
- Firefox Mobile

## 🔒 Bezpieczeństwo

- **Transparentny kod** - wszystko widoczne przed uruchomieniem
- **Brak zależności zewnętrznych** - tylko standardowa biblioteka Python
- **Lokalny sandbox** - aplikacja działa lokalnie
- **Docker isolation** - dodatkowa izolacja w kontenerze

## 🎨 Funkcje UI

- **Responsywny design** - dostosowuje się do ekranu
- **Animacje** - płynne przejścia i efekty
- **Powiadomienia systemowe** - natywne notyfikacje
- **Tryb ciemny** - automatyczne wykrywanie preferencji
- **Skróty klawiszowe** - Ctrl/Cmd + 1,2,3,i

## 📊 Dane biznesowe

Dashboard zawiera:
- 5 przykładowych faktur
- Łączna wartość: 13,900 PLN  
- Status płatności: 60% opłacone
- Filtrowanie po statusie
- Statystyki w czasie rzeczywistym

## 🛠️ Dla deweloperów

### Struktura pliku
```
testapp.eml.py
├── Python script (wykonywalna część)
├── EML headers (MIME metadata)
├── HTML (index.html)
├── CSS (style.css)
├── JavaScript (script.js)
├── Images (thumbnails)
├── Dockerfile
└── Metadata (JSON)
```

### Customization
Możesz zmodyfikować:
- Dane biznesowe w `script.js`
- Styling w sekcji CSS
- Layout w sekcji HTML
- Konfigurację Docker w Dockerfile

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź czy Python 3.6+ jest zainstalowany
2. Użyj odpowiedniego launchera dla swojej platformy
3. Sprawdź [install-python.md](install-python.md) dla instrukcji instalacji

## 📄 Licencja

Ten projekt jest dostępny na licencji Apache 2.0

Możesz go swobodnie używać, modyfikować i dystrybuować.

---

**🌍 Universal EML WebApp - One file, all platforms!**
```

## 🎯 Podsumowanie rozwiązania

Stworzyłem **kompletne uniwersalne rozwiązanie** składające się z:

### 1. **Główny plik** - `testapp.eml.py`
- Działa na **wszystkich platformach** (Windows, macOS, Linux)
- **Python 3.6+** jako wspólny mianownik
- **Automatyczne wykrywanie platformy**
- **GUI fallback** dla Windows (tkinter dialog)
- **Inteligentne znajdowanie Python** na każdym systemie

### 2. **Launchery platformowe**
- `run-windows.bat` - Windows batch z menu wyboru
- `run-macos.command` - macOS z osascript dialogs
- `run-linux.sh` - Linux z wykrywaniem dystrybucji

### 3. **Dokumentacja**
- Kompletne instrukcje instalacji Python
- README z opisem funkcji
- Przykłady użytkowania dla każdej platformy

### 🌟 **Kluczowe zalety:**

✅ **Jedna komenda** - `python3 testapp.eml.py`  
✅ **Zero instalacji** - tylko Python (standardowo dostępny)  
✅ **Inteligentne wykrywanie** - platformy, Python, Docker  
✅ **Graceful degradation** - zawsze znajdzie sposób działania  
✅ **User-friendly** - GUI dialogs, powiadomienia systemowe  
✅ **Cross-platform UX** - dostosowany interfejs do każdej platformy  

Ten format **EML WebApp** to rewolucyjne podejście - **jeden plik uniwersalny**, który działa dosłownie wszędzie gdzie jest Python! 🚀



















