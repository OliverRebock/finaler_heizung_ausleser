#!/bin/bash
# Pi5 Heizungs-Messer - Auto-Deploy from GitHub
# ==============================================

set -e  # Exit on error

echo "🚀 Pi5 Heizungs-Messer - Automatische GitHub Installation"
echo "=========================================================="
echo ""

# Configuration
GITHUB_REPO="https://github.com/OliverRebock/finaler_heizung_ausleser.git"
PROJECT_DIR="/home/pi/finaler_heizung_ausleser"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if running on Raspberry Pi
log "🔍 Prüfe System..."
if [[ ! -f /proc/device-tree/model ]] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    warning "Nicht auf Raspberry Pi erkannt - Installation wird fortgesetzt"
else
    PI_MODEL=$(cat /proc/device-tree/model | tr -d '\0')
    log "✅ Erkannt: $PI_MODEL"
fi

# Check internet connection
log "🌐 Prüfe Internet-Verbindung..."
if ! ping -c 1 github.com &> /dev/null; then
    error "Keine Internet-Verbindung zu GitHub"
fi
log "✅ Internet-Verbindung OK"

# Install basic dependencies
log "📦 Installiere grundlegende Abhängigkeiten..."
sudo apt update
sudo apt install -y git curl wget nano

# Check if Git is configured
log "🔧 Prüfe Git-Konfiguration..."
if ! git config --global user.name &> /dev/null; then
    warning "Git user.name nicht konfiguriert"
    read -p "Git Benutzername eingeben: " git_name
    git config --global user.name "$git_name"
fi

if ! git config --global user.email &> /dev/null; then
    warning "Git user.email nicht konfiguriert"
    read -p "Git E-Mail eingeben: " git_email
    git config --global user.email "$git_email"
fi

# Handle existing directory
if [ -d "$PROJECT_DIR" ]; then
    warning "Projekt-Verzeichnis existiert bereits: $PROJECT_DIR"
    read -p "Soll das Verzeichnis überschrieben werden? (y/N): " overwrite
    
    if [[ $overwrite =~ ^[Yy]$ ]]; then
        log "🗑️ Entferne altes Verzeichnis..."
        rm -rf "$PROJECT_DIR"
    else
        # Try to update existing repo
        log "🔄 Versuche existierendes Repository zu aktualisieren..."
        cd "$PROJECT_DIR"
        if git remote -v | grep -q "$GITHUB_REPO"; then
            log "📥 Aktualisiere Repository..."
            git fetch origin
            git reset --hard origin/$BRANCH
            log "✅ Repository aktualisiert"
        else
            error "Existierendes Verzeichnis ist kein gültiges Git-Repository"
        fi
    fi
fi

# Clone repository if not exists
if [ ! -d "$PROJECT_DIR" ]; then
    log "📥 Klone Repository von GitHub..."
    git clone -b $BRANCH "$GITHUB_REPO" "$PROJECT_DIR"
    log "✅ Repository geklont"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Verify project structure
log "🔍 Prüfe Projekt-Struktur..."
required_files=("requirements.txt" "scripts/install_dependencies.sh" "config/docker-compose.yml" "src/sensor_reader.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        error "Erforderliche Datei fehlt: $file"
    fi
done
log "✅ Projekt-Struktur vollständig"

# Make scripts executable
log "🔧 Mache Scripts ausführbar..."
chmod +x scripts/*.sh
chmod +x scripts/*.py
log "✅ Scripts ausführbar gemacht"

# Run installation
log "🛠️ Starte Installation der Abhängigkeiten..."
bash scripts/install_dependencies.sh

# Show next steps
echo ""
log "🎉 GITHUB-DEPLOYMENT ERFOLGREICH!"
echo ""
info "📁 Projekt-Verzeichnis: $PROJECT_DIR"
info "🌐 GitHub Repository: $GITHUB_REPO"
echo ""
info "📝 Nächste Schritte:"
echo "   1. cd $PROJECT_DIR"
echo "   2. bash scripts/deploy_docker.sh     # Docker Services starten"
echo "   3. source venv/bin/activate          # Python Environment aktivieren"
echo "   4. python scripts/test_sensors.py    # Hardware testen"
echo "   5. nano config/config.ini            # Konfiguration anpassen"
echo "   6. python src/sensor_reader.py       # Service starten"
echo ""
info "🔄 Repository Updates:"
echo "   cd $PROJECT_DIR && git pull origin $BRANCH"
echo ""
info "🐳 Services nach Installation verfügbar:"
echo "   InfluxDB: http://$(hostname -I | awk '{print $1}'):8086"
echo "   Grafana:  http://$(hostname -I | awk '{print $1}'):3000"
echo ""
info "📚 Dokumentation:"
echo "   README.md - Vollständige Anleitung"
echo "   QUICK_START.md - Schnellstart"
echo "   DOCKER_COMPATIBILITY.md - Docker-Info"
