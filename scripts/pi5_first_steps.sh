#!/bin/bash
# 🏠 Pi5 Heizungs-Messer - Erste Schritte Script
# ==============================================

echo "🏠 Pi5 Heizungs-Messer - Setup Check"
echo "====================================="

# Aktuelles Verzeichnis prüfen
CURRENT_DIR=$(pwd)
EXPECTED_DIR="/home/pi/Heizung_auslesen"

echo ""
echo "📍 Verzeichnis Check:"
echo "   Aktuell:   $CURRENT_DIR"
echo "   Erwartet:  $EXPECTED_DIR"

if [ "$CURRENT_DIR" != "$EXPECTED_DIR" ]; then
    echo "   ❌ Falsches Verzeichnis!"
    echo ""
    echo "🔄 Wechsle ins richtige Verzeichnis..."
    
    if [ -d "$EXPECTED_DIR" ]; then
        cd "$EXPECTED_DIR"
        echo "   ✅ Erfolgreich gewechselt zu: $(pwd)"
    else
        echo "   ❌ Projekt-Verzeichnis nicht gefunden!"
        echo "   💡 Führe zuerst aus:"
        echo "      cd /home/pi"
        echo "      git clone https://github.com/OliverRebock/finaler_heizung_ausleser.git Heizung_auslesen"
        exit 1
    fi
else
    echo "   ✅ Korrektes Verzeichnis!"
fi

echo ""
echo "🔍 System Check:"

# Git Repository Check
if [ -d ".git" ]; then
    echo "   ✅ Git Repository vorhanden"
    
    # Neueste Version holen
    echo "   🔄 Hole neueste Version von GitHub..."
    git pull origin main
else
    echo "   ❌ Kein Git Repository - Repository neu klonen!"
    exit 1
fi

# Python Virtual Environment Check
if [ -d "venv" ]; then
    echo "   ✅ Python Virtual Environment vorhanden"
else
    echo "   ⚠️ Python Virtual Environment fehlt"
    echo "   🔄 Erstelle Virtual Environment..."
    python3 -m venv venv
    echo "   ✅ Virtual Environment erstellt"
fi

# Dependencies Check
echo "   🔄 Aktiviere Virtual Environment..."
source venv/bin/activate

echo "   🔍 Prüfe Python Dependencies..."
if pip list | grep -q "adafruit-circuitpython-dht"; then
    echo "   ✅ Python Dependencies installiert"
else
    echo "   ⚠️ Dependencies fehlen"
    echo "   🔄 Installiere Dependencies..."
    bash scripts/install_dependencies.sh
fi

echo ""
echo "🌡️ Hardware Tests:"

# 1-Wire Interface Check
echo "   🔍 1-Wire Interface..."
if [ -d "/sys/bus/w1/devices" ]; then
    echo "   ✅ 1-Wire Interface aktiv"
    
    # DS18B20 Sensoren zählen
    DS_COUNT=$(ls /sys/bus/w1/devices/ | grep "^28-" | wc -l)
    echo "   📊 DS18B20 Sensoren gefunden: $DS_COUNT"
    
    if [ $DS_COUNT -gt 0 ]; then
        echo "   ✅ DS18B20 Sensoren verfügbar"
    else
        echo "   ⚠️ Keine DS18B20 Sensoren erkannt"
    fi
else
    echo "   ❌ 1-Wire Interface nicht aktiv"
    echo "   💡 Aktiviere mit: sudo raspi-config → Interface Options → 1-Wire"
fi

# GPIO Permissions Check
echo "   🔍 GPIO Permissions..."
if [ -w "/sys/class/gpio/export" ]; then
    echo "   ✅ GPIO Schreibberechtigung vorhanden"
else
    echo "   ❌ Keine GPIO Schreibberechtigung"
    echo "   💡 Führe aus: bash scripts/fix_gpio_permissions.sh && sudo reboot"
fi

echo ""
echo "🚀 Bereit für Tests!"
echo "==================="
echo ""
echo "📋 Verfügbare Test-Befehle:"
echo "   DS18B20 Sensoren:  python3 scripts/test_sensors_direct.py"
echo "   DHT22 sicher:      python3 scripts/test_dht22_safe.py"
echo "   DHT22 alternativ:  python3 scripts/test_dht22_simple.py"
echo ""
echo "🐳 Docker Services:"
echo "   Starten:           bash scripts/deploy_docker.sh"
echo "   Status prüfen:     cd config && docker-compose ps"
echo ""
echo "📊 Web-Interfaces (nach Docker Start):"
echo "   InfluxDB:          http://$(hostname -I | awk '{print $1}'):8086"
echo "   Grafana:           http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "🔧 Hilfe bei Problemen:"
echo "   GPIO Permissions:  bash scripts/fix_gpio_permissions.sh"
echo "   Repository Update: bash scripts/update_repository.sh"
echo ""
echo "✅ Setup Check abgeschlossen!"
