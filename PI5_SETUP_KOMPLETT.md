# 🏠 Raspberry Pi 5 - KOMPLETTER SETUP von Null
# =============================================

Diese Anleitung führt dich von einem frischen Raspberry Pi 5 zur voll funktionsfähigen Heizungs-Überwachung!

## 📋 Was du brauchst

### Hardware:
- 🔲 Raspberry Pi 5 (4GB oder 8GB)
- 🔲 MicroSD-Karte (32GB+)  
- 🔲 8x DS18B20 Temperatursensoren
- 🔲 1x DHT22 Temperatur/Luftfeuchtigkeitssensor
- 🔲 Breadboard & Jumper-Kabel
- 🔲 4.7kΩ Pull-up Widerstand (für DS18B20)
- 🔲 10kΩ Pull-up Widerstand (für DHT22)

### Software:
- 🔲 Raspberry Pi OS (aktuell)
- 🔲 SSH-Zugang oder Monitor/Tastatur

## ⚡ PHASE 1: Raspberry Pi OS Setup

### 1.1 Raspberry Pi OS installieren
```bash
# Falls noch nicht installiert, verwende Raspberry Pi Imager
# Aktiviere SSH und WiFi im Imager!
```

### 1.2 Erste Anmeldung und Update
```bash
# SSH Verbindung:
ssh pi@192.168.X.X

# System aktualisieren (WICHTIG!)
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 1.3 Grundlegende Tools installieren
```bash
# Nach Reboot wieder einloggen
sudo apt install -y git python3 python3-pip python3-venv curl wget htop
```

## ⚡ PHASE 2: Hardware Interface aktivieren

### 2.1 1-Wire Interface für DS18B20
```bash
sudo raspi-config
```
**Navigation:**
1. `3 Interface Options`
2. `I7 1-Wire`  
3. `Yes` (Would you like the one-wire interface to be enabled?)
4. `Ok`
5. `Finish`
6. `Yes` (Would you like to reboot now?)

### 2.2 Nach Reboot: Module prüfen
```bash
# Wieder einloggen nach Reboot
lsmod | grep w1

# Sollte zeigen:
# w1_therm
# w1_gpio
# wire

# Falls nicht vorhanden, manuell laden:
sudo modprobe w1-gpio w1-therm
```

### 2.3 GPIO Permissions einrichten
```bash
sudo usermod -aG gpio pi
sudo usermod -aG i2c pi
sudo usermod -aG spi pi
sudo reboot
```

## ⚡ PHASE 3: Hardware anschließen

### 3.1 DS18B20 Sensoren (1-Wire Bus)
```
Anschluss Schema:
DS18B20 Pin 1 (GND)  → Pi Pin 6  (GND)
DS18B20 Pin 2 (DATA) → Pi Pin 7  (GPIO 4) + 4.7kΩ Pull-up zu 3.3V
DS18B20 Pin 3 (VDD)  → Pi Pin 1  (3.3V)

Hinweis: Alle 8x DS18B20 parallel an denselben 1-Wire Bus!
```

### 3.2 DHT22 Sensor  
```
Anschluss Schema:
DHT22 Pin 1 (VDD)  → Pi Pin 1  (3.3V)
DHT22 Pin 2 (DATA) → Pi Pin 12 (GPIO 18) + 10kΩ Pull-up zu 3.3V
DHT22 Pin 3 (NC)   → Nicht angeschlossen
DHT22 Pin 4 (GND)  → Pi Pin 6  (GND)

⚠️ WICHTIG: GPIO 18 (Pin 12) verwenden!
```

### 3.3 Hardware-Test (vor Software)
```bash
# 1-Wire Devices prüfen
ls -la /sys/bus/w1/devices/

# Sollte zeigen:
# 28-xxxxxxxxxxxx (für jeden DS18B20)
# w1_bus_master1

# GPIO Status prüfen
gpio readall
```

## ⚡ PHASE 4: Software Installation

### 4.1 Projekt herunterladen
```bash
cd /home/pi
git clone https://github.com/OliverRebock/finaler_heizung_ausleser.git Heizung_auslesen
cd Heizung_auslesen
```

### 4.2 Dependencies installieren
```bash
# Automatische Installation
bash scripts/install_dependencies.sh

# Warten bis fertig... (kann 5-15 Minuten dauern)
```

### 4.3 Erste Hardware-Tests
```bash
# ⚠️ WICHTIG: In das Projekt-Verzeichnis wechseln!
cd /home/pi/Heizung_auslesen

# DS18B20 Test (sollte alle 8 Sensoren finden)
python3 scripts/test_sensors_direct.py

# DHT22 sicherer Test
python3 scripts/test_dht22_safe.py
```

## ⚡ PHASE 5: Docker Installation

### 5.1 Docker installieren
```bash
# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Pi User zu Docker Gruppe hinzufügen
sudo usermod -aG docker pi

# Docker Compose installieren (falls nicht automatisch)
sudo apt install -y docker-compose

# Reboot für Gruppenmitgliedschaft
sudo reboot
```

### 5.2 Docker testen
```bash
# Nach Reboot einloggen
docker --version
docker-compose --version

# Test Container
docker run hello-world
```

## ⚡ PHASE 6: Services starten

### 6.1 Docker Services deployen
```bash
cd /home/pi/Heizung_auslesen
bash scripts/deploy_docker.sh
```

### 6.2 Services prüfen
```bash
cd config
docker-compose ps

# Sollte zeigen:
# influxdb -> running
# grafana  -> running
```

### 6.3 Service Logs prüfen
```bash
# InfluxDB Logs
docker-compose logs -f influxdb

# Grafana Logs (in neuem Terminal)
docker-compose logs -f grafana
```

## ⚡ PHASE 7: Konfiguration

### 7.1 InfluxDB Setup (Erstmalig)
```bash
# Browser öffnen: http://PI_IP_ADRESSE:8086
# Setup Wizard:
```
- **Username**: `admin`
- **Password**: `admin123`  
- **Organization**: `HeizungsMesher`
- **Bucket Name**: `heating_data`

### 7.2 Grafana Setup
```bash
# Browser öffnen: http://PI_IP_ADRESSE:3000
# Login:
```
- **Username**: `admin`
- **Password**: `admin123`

**Data Source hinzufügen:**
1. Configuration → Data Sources → Add data source
2. InfluxDB auswählen
3. URL: `http://influxdb:8086`
4. Organization: `HeizungsMesher`
5. Token: (aus InfluxDB kopieren)
6. Bucket: `heating_data`

### 7.3 Sensor Reader starten
```bash
cd /home/pi/Heizung_auslesen
source venv/bin/activate
python src/sensor_reader.py

# Sollte zeigen:
# ✅ 8x DS18B20 Sensoren gefunden
# ✅ DHT22 Sensor bereit
# ✅ InfluxDB Verbindung OK
# 📊 Datensammlung gestartet...
```

## 🎯 PHASE 8: Autostart einrichten

### 8.1 Systemd Service erstellen
```bash
sudo nano /etc/systemd/system/heizung-messer.service
```

**Service File Inhalt:**
```ini
[Unit]
Description=Heizung Sensor Reader
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Heizung_auslesen
ExecStart=/home/pi/Heizung_auslesen/venv/bin/python src/sensor_reader.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8.2 Service aktivieren
```bash
sudo systemctl daemon-reload
sudo systemctl enable heizung-messer.service
sudo systemctl start heizung-messer.service

# Status prüfen
sudo systemctl status heizung-messer.service
```

## 🎉 ERFOLGREICH! Was du jetzt hast:

### ✅ Hardware:
- 8x DS18B20 Temperatursensoren aktiv
- 1x DHT22 Temperatur/Luftfeuchtigkeit aktiv  
- Alle 30 Sekunden automatische Messungen

### ✅ Software:
- InfluxDB sammelt alle Sensor-Daten
- Grafana zeigt Live-Dashboards
- Automatischer Start bei Boot
- MQTT Integration für Home Assistant bereit

### ✅ Web-Interfaces:
- **InfluxDB**: `http://PI_IP:8086`
- **Grafana**: `http://PI_IP:3000`

## 🔧 Wartung & Monitoring

### Service-Status prüfen:
```bash
sudo systemctl status heizung-messer
docker-compose ps
```

### Logs anzeigen:
```bash
sudo journalctl -u heizung-messer -f
docker-compose logs -f
```

### Service neu starten:
```bash
sudo systemctl restart heizung-messer
docker-compose restart
```

## 🚨 Troubleshooting

### DS18B20 nicht erkannt:
```bash
# Module neu laden
sudo modprobe -r w1-therm w1-gpio
sudo modprobe w1-gpio w1-therm

# Hardware prüfen
ls /sys/bus/w1/devices/
```

### DHT22 Probleme:
```bash
# Alternative Tests
python3 scripts/test_dht22_safe.py
python3 scripts/test_dht22_simple.py

# GPIO Permissions fix
bash scripts/fix_gpio_permissions.sh
sudo reboot
```

### Docker Probleme:
```bash
# Docker neu starten
sudo systemctl restart docker
cd /home/pi/Heizung_auslesen/config
docker-compose down
docker-compose up -d
```

---

## 🎯 Das war's! 

Du hast jetzt ein voll funktionsfähiges Pi5 Heizungs-Monitoring System! 

**Nächste Schritte:**
- Grafana Dashboards anpassen
- Home Assistant MQTT Integration
- Alarme und Benachrichtigungen einrichten

🏠📊 **Viel Spaß mit deinem Smart Home Heating Monitor!**
