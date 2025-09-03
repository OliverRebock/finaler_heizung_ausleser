#!/bin/bash
# Pi5 Heizungs-Messer Docker Deployment Script
# ============================================

set -e  # Exit on error

echo "🐳 Pi5 Heizungs-Messer - Docker Services starten..."
echo ""

# Check if we're in the right directory
if [ ! -f "config/docker-compose.yml" ]; then
    echo "❌ Fehler: config/docker-compose.yml nicht gefunden"
    echo "Bitte Script aus dem Projekt-Root-Verzeichnis ausführen"
    echo ""
    echo "🚀 Projekt von GitHub installieren:"
    echo "curl -fsSL https://raw.githubusercontent.com/OliverRebock/finaler_heizung_ausleser/main/scripts/github_deploy.sh | bash"
    exit 1
fi

# Docker und Docker Compose Version prüfen
echo "🔍 Prüfe Docker Installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker nicht gefunden. Bitte zuerst install_dependencies.sh ausführen"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose nicht gefunden. Bitte zuerst install_dependencies.sh ausführen"
    exit 1
fi

# Versionen anzeigen
DOCKER_VERSION=$(docker --version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
COMPOSE_VERSION=$(docker-compose --version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')

echo "✅ Docker: $DOCKER_VERSION"
echo "✅ Docker Compose: $COMPOSE_VERSION"
echo ""

# Check Docker daemon
echo "🔄 Prüfe Docker Daemon..."
if ! docker info &> /dev/null; then
    echo "❌ Docker Daemon läuft nicht. Starte Docker Service..."
    sudo systemctl start docker
    sleep 3
    
    if ! docker info &> /dev/null; then
        echo "❌ Docker Daemon konnte nicht gestartet werden"
        exit 1
    fi
fi
echo "✅ Docker Daemon läuft"
echo ""

# Create data directories if they don't exist
echo "📁 Erstelle Daten-Verzeichnisse..."
mkdir -p data/influxdb
mkdir -p data/grafana
echo "✅ Verzeichnisse erstellt"
echo ""

# Optional: Cleanup old containers
read -p "🧹 Sollen alte Container gestoppt und entfernt werden? (y/N): " cleanup
if [[ $cleanup =~ ^[Yy]$ ]]; then
    echo "Stoppe und entferne alte Container..."
    cd config
    docker-compose down --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    cd ..
    echo "✅ Cleanup abgeschlossen"
fi
echo ""

# Start services
echo "🚀 Starte Docker Services..."
cd config

# Pull latest images
echo "📥 Lade neueste Images..."
docker-compose pull

echo ""
echo "⚡ Starte Container (dies kann bis zu 2 Minuten dauern)..."
docker-compose up -d

echo ""
echo "⏳ Warte auf Service-Bereitschaft..."

# Wait for InfluxDB to be healthy
echo -n "📊 InfluxDB startet"
for i in {1..60}; do
    if docker-compose exec influxdb curl -f http://localhost:8086/health &>/dev/null; then
        echo " ✅"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Grafana
echo -n "📈 Grafana startet"
for i in {1..30}; do
    if curl -f http://localhost:3000 &>/dev/null; then
        echo " ✅"
        break
    fi
    echo -n "."
    sleep 2
done

cd ..

echo ""
echo "🎉 DEPLOYMENT ERFOLGREICH!"
echo ""
echo "📊 Services verfügbar unter:"
echo "   InfluxDB: http://localhost:8086"
echo "   Grafana:  http://localhost:3000"
echo ""
echo "🔧 Standard-Zugangsdaten:"
echo "   InfluxDB: admin / adminpassword123"
echo "   Grafana:  admin / admin"
echo ""
echo "📝 Nächste Schritte:"
echo "   1. InfluxDB Setup: http://localhost:8086"
echo "   2. Grafana Login: http://localhost:3000"
echo "   3. Sensor Config in config/config.ini anpassen"
echo "   4. Sensoren testen: python scripts/test_sensors.py"
echo "   5. Service starten: python src/sensor_reader.py"
echo ""
echo "🛠️ Container-Management:"
echo "   Status:   docker-compose -f config/docker-compose.yml ps"
echo "   Logs:     docker-compose -f config/docker-compose.yml logs -f"
echo "   Stoppen:  docker-compose -f config/docker-compose.yml down"
echo "   Nestart:  docker-compose -f config/docker-compose.yml restart"
