# 🏠 Pi5 Heizungs-Messer - Von Null auf Hundert!
# ===============================================

## 🎯 KOMPLETTER NEU-SETUP für Raspberry Pi 5

Diese Anleitung führt dich von einem frischen Pi5 zur voll funktionsfähigen Heizungs-Überwachung!

## 📋 Hardware-Vorbereitung

**Sensoren anschließen:**
- 🌡️ **8x DS18B20** → 1-Wire Bus an **GPIO 4** (Pin 7)
- 🌡️💧 **1x DHT22** → Digital Pin an **GPIO 17** (Pin 11) ⚠️ NICHT GPIO 18!
- 🔌 **3.3V & GND** → Entsprechende Pins

## ⚡ SCHRITT 1: Raspberry Pi 5 Grundsetup

### 1.1 System aktualisieren
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 1.2 Git und Python installieren
```bash
sudo apt install -y git python3 python3-pip python3-venv
```

### 1.3 1-Wire Interface aktivieren
```bash
sudo raspi-config
# → Interface Options → 1-Wire → Enable → Yes → Finish
sudo reboot
```

### 1.4 GPIO Permissions einrichten
```bash
sudo usermod -aG gpio pi
sudo usermod -aG i2c pi
sudo reboot
```

## ⚡ SCHRITT 2: Projekt herunterladen

### 2.1 Repository klonen
```bash
cd /home/pi
git clone https://github.com/OliverRebock/finaler_heizung_ausleser.git Heizung_auslesen
cd Heizung_auslesen
```

### 2.2 Dependencies installieren
```bash
# Python Virtual Environment erstellen und aktivieren
python3 -m venv heizung_venv
source heizung_venv/bin/activate

# Dependencies installieren
bash scripts/install_dependencies.sh
```

## ⚡ SCHRITT 3: Hardware testen

⚠️ **WICHTIG: Virtual Environment aktivieren vor jedem Test!**
```bash
cd /home/pi/Heizung_auslesen
source heizung_venv/bin/activate
```

### 3.1 DS18B20 Sensoren prüfen (sollten funktionieren)
```bash
python3 scripts/test_sensors_direct.py
```

### 3.2 DHT22 sicher testen (falls Probleme)
```bash
python3 scripts/test_dht22_safe.py
```

## ⚡ SCHRITT 4: Docker Services

### 4.1 Docker installieren (falls nicht vorhanden)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
sudo reboot
```

### 4.2 Services starten
```bash
cd /home/pi/Heizung_auslesen
bash scripts/deploy_docker.sh
```

### 4.3 Services prüfen
```bash
cd config
docker-compose ps
```

## ⚡ SCHRITT 5: Konfiguration

### 5.1 InfluxDB Setup (Erststart)
```bash
# Browser: http://PI_IP_ADRESSE:8086
# Username: admin
# Password: admin123
# Organization: HeizungsMesher
# Bucket: heating_data
```

### 5.2 Sensor-Reader starten
```bash
cd /home/pi/Heizung_auslesen
source venv/bin/activate
python src/sensor_reader.py
```

## 📊 Wichtige URLs

- **InfluxDB**: http://PI_IP_ADRESSE:8086
- **Grafana**: http://PI_IP_ADRESSE:3000 (admin/admin123)

## 🔧 Docker Befehle

```bash
cd /home/pi/Heizung_auslesen/config

# Services starten
docker-compose up -d

# Status prüfen  
docker-compose ps

# Logs anzeigen
docker-compose logs -f influxdb
docker-compose logs -f grafana

# Services stoppen
docker-compose down

# Services neu starten
docker-compose restart
```

## 🚨 Troubleshooting

### Problem: DS18B20 nicht erkannt
```bash
# 1-Wire Module prüfen
lsmod | grep w1
# Falls leer:
sudo modprobe w1-gpio w1-therm

# Devices prüfen
ls -la /sys/bus/w1/devices/
```

### Problem: DHT22 hängt
```bash
# Sichere Tests verwenden
python3 scripts/test_dht22_safe.py
python3 scripts/test_dht22_simple.py

# GPIO Fix anwenden
bash scripts/fix_gpio_permissions.sh
sudo reboot
```

### Problem: Docker Services starten nicht
```bash
# Docker Status prüfen
sudo systemctl status docker

# Docker neu starten
sudo systemctl restart docker

# Disk Space prüfen
df -h
```

## 🎯 Erwartete Ergebnisse

### ✅ Erfolgreicher Setup:
- 8x DS18B20 Sensoren erkannt
- DHT22 liefert Temperatur + Luftfeuchtigkeit
- InfluxDB sammelt alle 30 Sekunden Daten
- Grafana zeigt Live-Dashboards

### 📈 Performance für Pi5:
- **Memory**: ~500MB-1GB
- **CPU**: <10% bei normalem Betrieb
- **Storage**: ~2GB für Logs und Daten
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
