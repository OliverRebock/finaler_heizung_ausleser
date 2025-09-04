🐍 Python Virtual Environment - Cheat Sheet
==========================================

## 🚀 Schnell-Start (Copy & Paste):

```bash
# 1. Ins Projekt-Verzeichnis wechseln
cd /home/pi/Heizung_auslesen

# 2. Virtual Environment aktivieren
source heizung_venv/bin/activate

# 3. Sensor Tests ausführen
python3 scripts/test_sensors_direct.py
python3 scripts/test_dht22_safe.py

# 4. Virtual Environment deaktivieren (optional)
deactivate
```

## 📋 Wichtige Befehle:

### ✅ **Virtual Environment erstellen** (nur einmal nötig):
```bash
cd /home/pi/Heizung_auslesen
python3 -m venv heizung_venv
```

### 🔄 **Virtual Environment aktivieren** (bei jeder Session):
```bash
source heizung_venv/bin/activate
```

### 📦 **Pakete installieren** (im aktivierten venv):
```bash
pip install -r requirements.txt
```

### 🔍 **Prüfen ob venv aktiv ist**:
```bash
which python3
# Sollte zeigen: /home/pi/Heizung_auslesen/heizung_venv/bin/python3
```

### ❌ **Virtual Environment deaktivieren**:
```bash
deactivate
```

## 🏠 **Heizungs-Projekt spezifische Befehle:**

### 🧪 **Sensor Tests** (immer im venv):
```bash
cd /home/pi/Heizung_auslesen
source heizung_venv/bin/activate

# DS18B20 + DHT22 Test
python3 scripts/test_sensors_direct.py

# Nur DHT22 (sichere Version)
python3 scripts/test_dht22_safe.py

# DHT22 alternative Implementation
python3 scripts/test_dht22_simple.py
```

### 🔧 **Installation von Grund auf:**
```bash
cd /home/pi
git clone https://github.com/OliverRebock/finaler_heizung_ausleser.git Heizung_auslesen
cd Heizung_auslesen

# Virtual Environment erstellen
python3 -m venv heizung_venv
source heizung_venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# GPIO Berechtigungen fix
bash scripts/fix_gpio_permissions.sh

# System reboot für GPIO Permissions
sudo reboot
```

### 📊 **Produktions-Betrieb:**
```bash
cd /home/pi/Heizung_auslesen
source heizung_venv/bin/activate

# Sensor Reader starten
python3 src/sensor_reader.py

# MQTT Bridge starten
python3 src/mqtt_bridge.py
```

## 🚨 **Häufige Fehler:**

❌ **"ModuleNotFoundError"** → Virtual Environment nicht aktiviert
✅ **Lösung:** `source heizung_venv/bin/activate`

❌ **"Permission denied"** → GPIO Permissions fehlen  
✅ **Lösung:** `bash scripts/fix_gpio_permissions.sh && sudo reboot`

❌ **"No such file or directory"** → Falsches Verzeichnis
✅ **Lösung:** `cd /home/pi/Heizung_auslesen`

## 💡 **Pro-Tipps:**

### 🔄 **Auto-Aktivierung in ~/.bashrc:**
```bash
echo "cd /home/pi/Heizung_auslesen && source heizung_venv/bin/activate" >> ~/.bashrc
```

### 📝 **Alias für schnellen Start:**
```bash
echo "alias heizung='cd /home/pi/Heizung_auslesen && source heizung_venv/bin/activate'" >> ~/.bashrc
source ~/.bashrc
```

Dann einfach: `heizung` tippen und du bist ready! 🚀

---
🏠🐍 **Happy Coding im Virtual Environment!**
