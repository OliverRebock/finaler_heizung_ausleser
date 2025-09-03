#!/bin/bash
# 🏠 Pi5 Heizungs-Messer - Erster Setup (Quick Install)
# ====================================================

set -e  # Exit bei Fehlern

echo "🏠 Pi5 Heizungs-Messer - Quick Setup"
echo "===================================="
echo ""

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funktionen
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️ $1"
}

# Check if running on Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    print_error "Dieses Script ist nur für Raspberry Pi gedacht!"
    exit 1
fi

print_status "Raspberry Pi erkannt!"

# Check Pi Model
PI_MODEL=$(cat /proc/device-tree/model)
print_info "Modell: $PI_MODEL"

echo ""
echo "📋 PHASE 1: System Setup"
echo "========================"

# System Update
print_info "Aktualisiere System..."
sudo apt update -y
sudo apt upgrade -y
print_status "System aktualisiert"

# Grundlegende Tools
print_info "Installiere grundlegende Tools..."
sudo apt install -y git python3 python3-pip python3-venv curl wget htop
print_status "Tools installiert"

echo ""
echo "📋 PHASE 2: Hardware Interface"
echo "=============================="

# Check 1-Wire
if lsmod | grep -q w1_therm; then
    print_status "1-Wire Interface bereits aktiv"
else
    print_warning "1-Wire Interface nicht aktiv!"
    print_info "Aktiviere 1-Wire Interface..."
    
    # Add to config.txt if not present
    if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt; then
        echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt
        print_info "1-Wire zu /boot/config.txt hinzugefügt"
    fi
    
    # Load modules
    sudo modprobe w1-gpio w1-therm
    print_warning "System-Reboot erforderlich für 1-Wire!"
fi

# GPIO Permissions
print_info "Richte GPIO Permissions ein..."
sudo usermod -aG gpio pi
sudo usermod -aG i2c pi
sudo usermod -aG spi pi
print_status "GPIO Permissions gesetzt"

echo ""
echo "📋 PHASE 3: Projekt Setup"
echo "========================="

# Check if already downloaded
if [ -d "/home/pi/Heizung_auslesen" ]; then
    print_warning "Projekt bereits vorhanden, aktualisiere..."
    cd /home/pi/Heizung_auslesen
    git pull origin main
    print_status "Projekt aktualisiert"
else
    print_info "Lade Projekt herunter..."
    cd /home/pi
    git clone https://github.com/OliverRebock/finaler_heizung_ausleser.git Heizung_auslesen
    cd Heizung_auslesen
    print_status "Projekt heruntergeladen"
fi

# Install Dependencies
print_info "Installiere Python Dependencies..."
if [ -f "scripts/install_dependencies.sh" ]; then
    bash scripts/install_dependencies.sh
    print_status "Dependencies installiert"
else
    print_error "install_dependencies.sh nicht gefunden!"
fi

echo ""
echo "📋 PHASE 4: Hardware Test"
echo "========================="

# Test Hardware
print_info "Teste Hardware..."

# DS18B20 Test
if [ -d "/sys/bus/w1/devices" ]; then
    DS18B20_COUNT=$(ls /sys/bus/w1/devices/ | grep "^28-" | wc -l)
    if [ $DS18B20_COUNT -gt 0 ]; then
        print_status "$DS18B20_COUNT DS18B20 Sensoren erkannt"
    else
        print_warning "Keine DS18B20 Sensoren gefunden"
        print_info "Prüfe Hardware-Anschluss und führe Reboot durch"
    fi
else
    print_warning "1-Wire Interface nicht verfügbar"
fi

# GPIO Test
if [ -d "/sys/class/gpio" ]; then
    print_status "GPIO Interface verfügbar"
else
    print_error "GPIO Interface nicht verfügbar!"
fi

echo ""
echo "📋 PHASE 5: Docker Check"
echo "========================"

# Check Docker
if command -v docker &> /dev/null; then
    print_status "Docker bereits installiert"
    DOCKER_VERSION=$(docker --version)
    print_info "$DOCKER_VERSION"
else
    print_info "Installiere Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker pi
    rm get-docker.sh
    print_status "Docker installiert"
    print_warning "Reboot erforderlich für Docker-Gruppenzugehörigkeit!"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_status "Docker Compose verfügbar"
    COMPOSE_VERSION=$(docker-compose --version)
    print_info "$COMPOSE_VERSION"
else
    print_info "Installiere Docker Compose..."
    sudo apt install -y docker-compose
    print_status "Docker Compose installiert"
fi

echo ""
echo "🎯 SETUP ZUSAMMENFASSUNG"
echo "========================"

print_status "System-Update durchgeführt"
print_status "Grundlegende Tools installiert"

if lsmod | grep -q w1_therm; then
    print_status "1-Wire Interface aktiv"
else
    print_warning "1-Wire Interface benötigt Reboot"
fi

print_status "GPIO Permissions konfiguriert"
print_status "Projekt heruntergeladen/aktualisiert"
print_status "Python Dependencies installiert"

if command -v docker &> /dev/null; then
    print_status "Docker installiert"
else
    print_warning "Docker Installation fehlgeschlagen"
fi

echo ""
echo "🚀 NÄCHSTE SCHRITTE"
echo "==================="

REBOOT_REQUIRED=false

if ! lsmod | grep -q w1_therm; then
    print_warning "1-Wire Interface benötigt Reboot"
    REBOOT_REQUIRED=true
fi

if ! groups pi | grep -q docker; then
    print_warning "Docker Gruppenzugehörigkeit benötigt Reboot"
    REBOOT_REQUIRED=true
fi

if [ "$REBOOT_REQUIRED" = true ]; then
    echo ""
    print_warning "SYSTEM-REBOOT ERFORDERLICH!"
    print_info "Führe aus: sudo reboot"
    print_info "Nach Reboot:"
    print_info "  cd /home/pi/Heizung_auslesen"
    print_info "  python3 scripts/test_sensors_direct.py"
    print_info "  bash scripts/deploy_docker.sh"
else
    echo ""
    print_status "Setup komplett! Teste jetzt die Hardware:"
    print_info "  cd /home/pi/Heizung_auslesen"
    print_info "  python3 scripts/test_sensors_direct.py"
    print_info "  python3 scripts/test_dht22_safe.py"
    print_info ""
    print_info "Dann starte die Services:"
    print_info "  bash scripts/deploy_docker.sh"
fi

echo ""
print_status "Setup Script abgeschlossen!"
echo "🏠📊 Viel Erfolg mit deinem Pi5 Heizungs-Monitor!"
