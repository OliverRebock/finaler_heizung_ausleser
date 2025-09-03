#!/bin/bash
# Pi5 Heizungs Messer - Dependency Installation Script
# ====================================================

set -e

echo "🏠 Pi5 Heizungs Messer - Installation Script"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Fehler: requirements.txt nicht gefunden"
    echo "Bitte Script aus dem Projekt-Root-Verzeichnis ausführen"
    echo ""
    echo "🚀 Automatische Installation von GitHub:"
    echo "curl -fsSL https://raw.githubusercontent.com/OliverRebock/finaler_heizung_ausleser/main/scripts/github_deploy.sh | bash"
    exit 1
fi

# Prüfe ob auf Raspberry Pi ausgeführt
if [[ ! -f /proc/device-tree/model ]] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️ Warnung: Nicht auf Raspberry Pi erkannt"
    echo "   Script wird trotzdem fortgesetzt..."
else
    PI_MODEL=$(cat /proc/device-tree/model | tr -d '\0')
    echo "✅ Erkannt: $PI_MODEL"
fi

# Prüfe für Pi5 spezifische Konfiguration
PI5_DETECTED=false
if grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo "🚀 Raspberry Pi 5 erkannt - optimierte Konfiguration"
    PI5_DETECTED=true
else
    echo "⚠️ Warnung: Nicht Pi5 erkannt - GPIO Pinout könnte abweichen"
fi

echo ""
echo "📦 Aktualisiere System Packages..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "🐍 Installiere Python Dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev

echo ""
echo "🔧 Installiere Hardware Dependencies..."
# GPIO Library für DHT22
sudo apt install -y python3-gpiozero python3-rpi.gpio

# 1-Wire Support für DS18B20 (Kernel Module, nicht Packages)
echo "🌡️ Konfiguriere 1-Wire Interface für DS18B20..."

# 1-Wire Module laden
sudo modprobe w1-gpio 2>/dev/null || echo "w1-gpio bereits geladen"
sudo modprobe w1-therm 2>/dev/null || echo "w1-therm bereits geladen"

# Module bei Boot laden
if ! grep -q "w1-gpio" /etc/modules 2>/dev/null; then
    echo "w1-gpio" | sudo tee -a /etc/modules
    echo "✅ w1-gpio zu /etc/modules hinzugefügt"
fi
if ! grep -q "w1-therm" /etc/modules 2>/dev/null; then
    echo "w1-therm" | sudo tee -a /etc/modules
    echo "✅ w1-therm zu /etc/modules hinzugefügt"
fi

# Device Tree Overlay aktivieren
REBOOT_REQUIRED=false
if [ -f "/boot/config.txt" ]; then
    if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt; then
        echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt
        echo "✅ 1-Wire Interface in /boot/config.txt aktiviert"
        REBOOT_REQUIRED=true
    else
        echo "✅ 1-Wire Interface bereits in config.txt aktiviert"
    fi
elif [ -f "/boot/firmware/config.txt" ]; then
    # Ubuntu 22.04+ auf Pi verwendet /boot/firmware/
    if ! grep -q "dtoverlay=w1-gpio" /boot/firmware/config.txt; then
        echo "dtoverlay=w1-gpio" | sudo tee -a /boot/firmware/config.txt
        echo "✅ 1-Wire Interface in /boot/firmware/config.txt aktiviert"
        REBOOT_REQUIRED=true
    else
        echo "✅ 1-Wire Interface bereits in firmware config.txt aktiviert"
    fi
else
    echo "⚠️ Boot config.txt nicht gefunden - manuelle 1-Wire Aktivierung erforderlich"
fi

echo ""
echo "📡 Installiere MQTT Client Tools..."
sudo apt install -y mosquitto-clients

echo ""
echo "🐳 Installiere Docker (für InfluxDB)..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installiert - Neuanmeldung erforderlich für Docker-Gruppe"
    rm -f get-docker.sh
else
    echo "✅ Docker bereits installiert"
fi

# Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
    echo "✅ Docker Compose $COMPOSE_VERSION gefunden"
    
    # Version Check (mindestens 1.27.0 für health conditions)
    if [[ $(echo "$COMPOSE_VERSION 1.27.0" | tr " " "\n" | sort -V | head -n1) == "1.27.0" ]]; then
        echo "✅ Docker Compose Version kompatibel"
    else
        echo "⚠️ Docker Compose Version zu alt - aktualisieren empfohlen"
        echo "Installiere neuere Version..."
        sudo apt update
        sudo apt install -y docker-compose
    fi
else
    echo "❌ Docker Compose nicht gefunden"
    echo "Installiere Docker Compose..."
    sudo apt install -y docker-compose
    echo "✅ Docker Compose installiert"
fi

echo ""
echo "🌡️ Erstelle Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual Environment erstellt"
else
    echo "✅ Virtual Environment bereits vorhanden"
fi

# Virtual Environment aktivieren
source venv/bin/activate

echo ""
echo "📥 Installiere Python Packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📋 Erstelle Konfigurationsdatei..."
if [ ! -f "config.ini" ]; then
    if [ -f "config/config.ini.example" ]; then
        cp config/config.ini.example config.ini
        echo "✅ config.ini aus Beispiel erstellt"
    else
        echo "⚠️ Beispiel-Konfiguration nicht gefunden"
    fi
else
    echo "✅ config.ini bereits vorhanden"
fi

echo ""
echo "✅ INSTALLATION ABGESCHLOSSEN!"
echo "==============================="
echo ""

# Zeige 1-Wire Status
echo "🔍 1-Wire Status prüfen..."
if [ -d "/sys/bus/w1/devices" ]; then
    DEVICE_COUNT=$(ls /sys/bus/w1/devices/ | grep -c "28-" 2>/dev/null || echo "0")
    if [ "$DEVICE_COUNT" -gt 0 ]; then
        echo "✅ $DEVICE_COUNT DS18B20 Sensor(en) erkannt:"
        ls /sys/bus/w1/devices/ | grep "28-" | head -3
    else
        echo "⚠️ Keine DS18B20 Sensoren erkannt"
        echo "   Prüfe Hardware-Verkabelung"
        if [ "$REBOOT_REQUIRED" = "true" ]; then
            echo "   Reboot erforderlich für 1-Wire Interface"
        fi
    fi
else
    echo "⚠️ 1-Wire Interface nicht aktiv"
    if [ "$REBOOT_REQUIRED" = "true" ]; then
        echo "   REBOOT erforderlich: sudo reboot"
    fi
fi

echo ""
echo "📋 Nächste Schritte:"
echo "   1. Hardware anschließen (DS18B20 an GPIO, DHT22 an GPIO 4)"
if [ "$REBOOT_REQUIRED" = "true" ]; then
    echo "   2. System neu starten: sudo reboot"
    echo "   3. Nach Reboot: bash scripts/deploy_docker.sh"
else
    echo "   2. Docker Services starten: bash scripts/deploy_docker.sh"
fi
echo "   4. Sensoren testen: python scripts/test_sensors.py"
echo "   5. Konfiguration anpassen: nano config/config.ini"
echo "   6. Service starten: python src/sensor_reader.py"
echo ""
echo "🔧 Wichtige Befehle:"
echo "   python scripts/test_sensors.py      # Hardware-Test"
echo "   bash scripts/deploy_docker.sh       # Docker Services"
echo "   docker-compose -f config/docker-compose.yml ps  # Container Status"
echo ""
echo "🌐 Nach Docker-Start verfügbar:"
echo "   InfluxDB: http://$(hostname -I | awk '{print $1}'):8086"
echo "   Grafana:  http://$(hostname -I | awk '{print $1}'):3000"
echo ""

# Reboot-Hinweis
if [ "$REBOOT_REQUIRED" = "true" ]; then
    echo "🔄 WICHTIG: Reboot erforderlich für 1-Wire Interface!"
    echo "   sudo reboot"
    echo ""
    echo "Nach dem Reboot fortfahren mit:"
    echo "   cd $(pwd)"
    echo "   bash scripts/deploy_docker.sh"
fi

echo "🎉 Installation erfolgreich abgeschlossen!"
