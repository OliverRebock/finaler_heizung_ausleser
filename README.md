# 🌡️ Pi5 Heizungs Messer - Projekt Heizung_Auslesen

Ein Python-basiertes Heizungsüberwachungssystem für Raspberry Pi 5 mit MQTT-Integration für Home Assistant.

## 🎯 Funktionen

- **Temperatursensoren**: DS18B20 1-Wire Sensoren für bis zu 8 Heizkreise
- **Umgebungsklima**: DHT22 für Heizraum-Temperatur und Luftfeuchtigkeit  
- **Datenspeicherung**: InfluxDB für Zeitreihen-Daten
- **Home Assistant**: MQTT Auto-Discovery Integration
- **Echtzeitüberwachung**: Kontinuierliche Datenerfassung
- **Robuste Hardware**: Optimiert für Raspberry Pi 5

## 🚀 Schnellstart

### 1. Installation auf Raspberry Pi 5

```bash
# Repository klonen
git clone <your-repo-url> ~/pi5-sensors
cd ~/pi5-sensors

# Python Virtual Environment einrichten
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Hardware Setup

**DS18B20 Temperatursensoren:**
- 1-Wire Interface am Pi5 aktivieren
- Sensoren an GPIO4 anschließen
- Pullup-Widerstand 4.7kΩ

**DHT22 Sensor:**
- Datenleitung an GPIO17
- 3.3V Versorgung
- Pullup-Widerstand 10kΩ (meist integriert)

### 3. Konfiguration

```bash
# Konfigurationsdatei erstellen
cp config.ini.example config.ini
nano config.ini
```

### 4. MQTT & Home Assistant Integration

```bash
# MQTT Bridge für Home Assistant installieren
wget https://raw.githubusercontent.com/OliverRebock/Heizung_small/main/install_mqtt_ultra_simple.sh
chmod +x install_mqtt_ultra_simple.sh
./install_mqtt_ultra_simple.sh
```

## 📁 Projektstruktur

```
Heizung_auslesen/
├── src/
│   ├── sensor_reader.py          # Hauptsensor-Klasse
│   ├── mqtt_bridge.py            # MQTT Home Assistant Bridge
│   ├── config_manager.py         # Konfigurationsverwaltung
│   └── hardware/
│       ├── ds18b20_sensor.py     # DS18B20 Temperatursensoren
│       └── dht22_sensor.py       # DHT22 Umgebungssensor
├── config/
│   ├── config.ini.example        # Beispielkonfiguration
│   └── docker-compose.yml        # InfluxDB Container
├── scripts/
│   ├── install_dependencies.sh   # Installation Script
│   ├── setup_hardware.sh         # Hardware Setup
│   └── test_sensors.py           # Sensor Tests
├── tests/
│   ├── test_sensors.py           # Unit Tests
│   └── test_mqtt.py              # MQTT Tests
├── docs/
│   └── installation_guide.md     # Detaillierte Anleitung
├── requirements.txt              # Python Dependencies
└── README.md                     # Diese Datei
```

## ⚙️ Konfiguration

### config.ini Beispiel:

```ini
[hardware]
# DS18B20 1-Wire Sensoren
ds18b20_enabled = true
ds18b20_sensors = 28-0000000001,28-0000000002

# DHT22 Umgebungssensor  
dht22_enabled = true
dht22_gpio = 17

[database]
# InfluxDB Einstellungen
host = localhost
port = 8086
token = pi5-token-2024
org = pi5org
bucket = sensors

[mqtt]
# MQTT Broker (Home Assistant)
broker = 192.168.1.100
port = 1883
username = homeassistant
password = mqtt_password
topic_prefix = pi5_heizung

[labels]
# Sensor Beschriftungen
28-0000000001 = HK1 Vorlauf
28-0000000002 = HK1 Rücklauf
dht22 = Heizraum
```

## 🧪 Testing & Debugging

```bash
# Einzelne Sensor-Tests
python src/test_sensors.py --dht22
python src/test_sensors.py --1wire

# MQTT Verbindung testen
python src/mqtt_bridge.py mqtt-test

# Vollständiger Systemtest
python src/test_sensors.py --all
```

## 🏠 Home Assistant Integration

Nach der MQTT-Installation erscheinen die Sensoren automatisch in Home Assistant:

- **Geräte & Services** → **MQTT**
- Suche nach "Pi5 Heizungs Messer"
- Sensoren werden automatisch erkannt

**Verfügbare Sensoren:**
- `sensor.hk1_vorlauf` - Heizkreis 1 Vorlauftemperatur
- `sensor.hk1_ruecklauf` - Heizkreis 1 Rücklauftemperatur  
- `sensor.heizraum_temperatur` - DHT22 Temperatur
- `sensor.heizraum_luftfeuchtigkeit` - DHT22 Luftfeuchtigkeit

## 📊 Monitoring

### Service Status prüfen:
```bash
sudo systemctl status pi5-sensors
sudo systemctl status pi5-mqtt-bridge
```

### Logs anzeigen:
```bash
sudo journalctl -u pi5-sensors -f
sudo journalctl -u pi5-mqtt-bridge -f
```

### MQTT Topics überwachen:
```bash
mosquitto_sub -h 192.168.1.100 -u homeassistant -P mqtt_password -t 'pi5_heizung/+/state'
```

## 🛠️ Troubleshooting

### Sensoren nicht gefunden:
```bash
# 1-Wire Interface prüfen
ls -la /sys/bus/w1/devices/

# DHT22 GPIO prüfen
gpio readall
```

### MQTT Probleme:
```bash
# MQTT Bridge reparieren
cd ~/pi5-sensors
wget https://raw.githubusercontent.com/OliverRebock/Heizung_small/main/fix_mqtt_import_error.sh
chmod +x fix_mqtt_import_error.sh
./fix_mqtt_import_error.sh
```

### InfluxDB Verbindung:
```bash
# InfluxDB Health Check
curl -I http://localhost:8086/health

# Docker Container prüfen
docker compose ps
```

## 📚 Weiterführende Links

- [Original Projekt Repository](https://github.com/OliverRebock/Heizung_small)
- [MQTT Integration Guide](https://github.com/OliverRebock/Heizung_small/blob/main/MQTT_INTEGRATION.md)
- [Home Assistant MQTT Discovery](https://www.home-assistant.io/docs/mqtt/discovery/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)

## 📝 Lizenz

Dieses Projekt ist für den persönlichen Gebrauch entwickelt. Basiert auf dem [Heizung_small](https://github.com/OliverRebock/Heizung_small) Projekt.

## 🆘 Support

Bei Problemen oder Fragen:
1. GitHub Issues erstellen
2. Logs mit `journalctl` prüfen
3. Sensor-Tests mit `test_sensors.py` ausführen
4. MQTT Verbindung mit `mqtt_bridge.py mqtt-test` testen
