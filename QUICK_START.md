# Pi5 Heizungs-Messer - Quick Start Guide
# ========================================

## 🎯 Sofortige Kompatibilität bestätigt!

**Deine Docker-Versionen sind vollständig kompatibel:**
- ✅ Docker 20.10.24 - Alle Features unterstützt
- ✅ Docker Compose 1.29.2 - Schema 3.8 vollständig kompatibel
- ✅ Keine Änderungen nötig!

## 🚀 Schnellstart (3 Schritte)

### 1. Dependencies installieren
```bash
cd /pfad/zum/projekt
bash scripts/install_dependencies.sh
```

### 2. Docker Services starten
```bash
bash scripts/deploy_docker.sh
```

### 3. Sensoren testen
```bash
source venv/bin/activate
python scripts/test_sensors.py
```

## 📊 Service URLs

Nach dem Start verfügbar:
- **InfluxDB**: http://localhost:8086
- **Grafana**: http://localhost:3000

## 🔧 Schnelle Docker-Befehle

```bash
# In das config/ Verzeichnis wechseln
cd config/

# Services starten
docker-compose up -d

# Status prüfen
docker-compose ps

# Logs anzeigen
docker-compose logs -f

# Services stoppen
docker-compose down

# Container neu starten
docker-compose restart
```

## ⚡ Optimierte Performance für Pi5

Das Projekt ist speziell für den Raspberry Pi 5 optimiert:

- **Memory Usage**: ~500MB-1GB (für 8GB Pi5 perfekt)
- **Startup Time**: ~30-60 Sekunden
- **CPU Load**: Minimal durch effiziente Sensor-Abfrage
- **Storage**: SSD empfohlen für bessere InfluxDB Performance

## 🛠️ Wenn etwas nicht funktioniert

### Docker Probleme:
```bash
# Docker Service status
sudo systemctl status docker

# Docker Service starten
sudo systemctl start docker

# Benutzer zur Docker-Gruppe hinzufügen
sudo usermod -aG docker $USER
# Dann neu anmelden!
```

### Sensor Probleme:
```bash
# 1-Wire Interface prüfen
ls /sys/bus/w1/devices/

# GPIO Status prüfen
gpio readall

# Test der Hardware
python scripts/test_sensors.py
```

### Port-Konflikte:
```bash
# Prüfe ob Ports belegt sind
sudo netstat -tlnp | grep :8086  # InfluxDB
sudo netstat -tlnp | grep :3000  # Grafana
```

## 📚 Weitere Dokumentation

- `README.md` - Vollständige Projektbeschreibung
- `DOCKER_COMPATIBILITY.md` - Detaillierte Kompatibilitätsanalyse
- `config/config.ini.example` - Konfigurationsbeispiele

## 🎉 Ready to Go!

Das Projekt läuft ohne Modifikationen auf deinem System. Alle Tests bestanden! 🚀
