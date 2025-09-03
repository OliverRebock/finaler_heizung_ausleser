#!/bin/bash
# Pi5 Heizungs Messer - Dependency Installation Script
# ====================================================

set -e

echo "🏠 Pi5 Heizungs Messer - Installation Script"
echo "============================================="

# Prüfe ob auf Raspberry Pi ausgeführt
if [[ ! -f /proc/device-tree/model ]] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️ Warnung: Nicht auf Raspberry Pi erkannt"
    echo "   Script wird trotzdem fortgesetzt..."
fi

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Fehler: requirements.txt nicht gefunden"
    echo "Bitte Script aus dem Projekt-Root-Verzeichnis ausführen"
    echo ""
    echo "🚀 Automatische Installation von GitHub:"
    echo "curl -fsSL https://raw.githubusercontent.com/OliverRebock/finaler_heizung_ausleser/main/scripts/github_deploy.sh | bash"
    exit 1
fi

# Prüfe Pi5 spezifisch
if grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo "✅ Raspberry Pi 5 erkannt"
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
sudo modprobe w1-gpio
sudo modprobe w1-therm

# Module bei Boot laden
if ! grep -q "w1-gpio" /etc/modules; then
    echo "w1-gpio" | sudo tee -a /etc/modules
fi
if ! grep -q "w1-therm" /etc/modules; then
    echo "w1-therm" | sudo tee -a /etc/modules
fi

# Device Tree Overlay aktivieren
if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt; then
    echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt
    echo "⚠️ REBOOT erforderlich für 1-Wire Interface!"
    REBOOT_REQUIRED=true
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
echo "📥 Installiere Python Packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ INSTALLATION ABGESCHLOSSEN!"

echo ""
echo "📋 Erstelle Konfigurationsdatei..."
if [ ! -f "config.ini" ]; then
    if [ -f "config/config.ini.example" ]; then
        cp config/config.ini.example config.ini
        echo "✅ config.ini aus Beispiel erstellt"
        echo "🔧 Bitte config.ini bearbeiten und anpassen!"
    else
        echo "⚠️ Beispiel-Konfiguration nicht gefunden"
    fi
else
    echo "✅ config.ini bereits vorhanden"
fi

echo ""
echo "🗄️ Starte InfluxDB Container..."
if [ -f "config/docker-compose.yml" ]; then
    cd config
    docker-compose up -d
    cd ..
    
    echo "⏳ Warte auf InfluxDB..."
    sleep 10
    
    # Health Check
    if curl -s http://localhost:8086/health > /dev/null; then
        echo "✅ InfluxDB Container läuft"
    else
        echo "⚠️ InfluxDB Container Status unbekannt"
    fi
else
    echo "⚠️ docker-compose.yml nicht gefunden"
fi

echo ""
echo "🧪 Führe Basis-Tests durch..."
python scripts/test_sensors.py --influxdb

echo ""
echo "🎉 Installation abgeschlossen!"
echo "==============================="
echo ""
echo "📋 Nächste Schritte:"
echo "   1. config.ini bearbeiten (Sensor-IDs, MQTT-Einstellungen)"
echo "   2. Sensoren testen: python scripts/test_sensors.py"
echo "   3. MQTT für Home Assistant einrichten"
echo "   4. Sensor Reader starten: python src/sensor_reader.py"
echo ""
echo "🔧 Wichtige Befehle:"
echo "   python scripts/test_sensors.py      # Alle Tests"
echo "   python src/sensor_reader.py --once  # Einmalige Messung"
echo "   python src/mqtt_bridge.py test      # MQTT Test"
echo ""
echo "🌐 Web Interfaces:"
echo "   InfluxDB: http://localhost:8086 (admin/password123)"
echo "   Grafana:  http://localhost:3000 (admin/admin)"
echo ""

# Neustart Empfehlung falls 1-Wire geändert wurde
if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt 2>/dev/null || [ ! -d "/sys/bus/w1/devices" ]; then
    echo "⚠️ NEUSTART ERFORDERLICH für 1-Wire Interface!"
    echo "   sudo reboot"
fi
