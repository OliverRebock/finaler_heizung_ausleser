🏠 Pi5 Heizungs-Messer - DHT22 Verkabelung
=========================================

## 📍 DHT22 Sensor Anschlüsse (Raspberry Pi 5)

### 🔌 DHT22 Pin-Belegung:
```
DHT22 Sensor (Vorderansicht):
┌─────────────────┐
│  1   2   3   4  │
│ VDD DATA NC GND │
└─────────────────┘
```

### 🔗 Raspberry Pi 5 Verbindungen (DEINE VERKABELUNG):

| DHT22 Pin | Beschreibung | Pi5 Pin | Pi5 GPIO | Kabel Farbe |
|-----------|--------------|---------|----------|-------------|
| Pin 1     | VDD (+)      | Pin 11  | GPIO 17  | Rot         |
| Pin 2     | DATA         | Pin 12  | GPIO 18  | Gelb/Grün   |
| Pin 3     | NC           | -       | -        | (nicht verwendet) |
| Pin 4     | GND          | Pin 39  | GPIO 20  | Schwarz     |

### 🔧 Zusätzlich benötigt:
- **10kΩ Widerstand** zwischen Pin 2 (DATA/GPIO 18) und Pin 1 (VDD/GPIO 17) als Pull-up

## 📊 Raspberry Pi 5 GPIO Layout (Deine Verkabelung):

```
Pi5 GPIO Header (relevante Pins):
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │  5  │  6  │  7  │  8  │  9  │ 10  │
│3.3V │ 5V  │GPIO2│ 5V  │GPIO3│ GND │GPIO4│TX   │ GND │ RX  │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ 11  │ 12  │ 13  │ 14  │ 15  │ 16  │ 17  │ 18  │ 19  │ 20  │
│GPIO17│GPIO18│GPIO27│GND │GPIO22│GPIO23│3.3V │GPIO24│MOSI │ GND │
│[VDD]│[DATA]│     │     │     │     │     │     │     │     │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ 21  │ 22  │ 23  │ 24  │ 25  │ 26  │ 27  │ 28  │ 29  │ 30  │
│MISO │GPIO25│SCLK │GPIO8│ GND │GPIO7│GPIO0│GPIO1│GPIO5│ GND │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ 31  │ 32  │ 33  │ 34  │ 35  │ 36  │ 37  │ 38  │ 39  │ 40  │
│GPIO6│GPIO12│GPIO13│GND │GPIO19│GPIO16│GPIO26│GPIO20│ GND │GPIO21│
│     │     │     │     │     │     │     │     │[GND]│     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

## ⚡ Schritt-für-Schritt Verkabelung (DEINE AKTUELLE VERKABELUNG):

### 1. **Stromversorgung (VDD)**
```
DHT22 Pin 1 (VDD) ──[Rot]──→ Pi5 Pin 11 (GPIO 17)
```

### 2. **Datenleitung (DATA) mit Pull-up**
```
DHT22 Pin 2 (DATA) ──[Gelb]──→ Pi5 Pin 12 (GPIO 18)
                     │
                     └──[10kΩ]──→ Pi5 Pin 11 (GPIO 17)
```

### 3. **Masse (GND)**
```
DHT22 Pin 4 (GND) ──[Schwarz]──→ Pi5 Pin 39 (GND)
```

### 4. **Pin 3 nicht anschließen**
```
DHT22 Pin 3 (NC) = Not Connected (frei lassen)
```

## 🧪 Test der Verkabelung:

Nach der Verkabelung teste mit:
```bash
cd /home/pi/Heizung_auslesen

# Python Virtual Environment aktivieren
source heizung_venv/bin/activate

# DHT22 Tests ausführen
python3 scripts/test_dht22_safe.py
```

## 🚨 WICHTIGER HINWEIS zu deiner Verkabelung:

⚠️ **PROBLEM:** Du verwendest GPIO 17 als Stromversorgung!
- GPIO Pins sind **nicht** für Stromversorgung gedacht
- Können nur wenige mA liefern
- DHT22 braucht 1-1.5mA im Betrieb
- **Kann funktionieren, ist aber nicht optimal**

### 🔧 BESSERE VERKABELUNG (empfohlen):
```
DHT22 Pin 1 (VDD) ──[Rot]──→ Pi5 Pin 1 oder 17 (3.3V Power)
DHT22 Pin 2 (DATA) ──[Gelb]──→ Pi5 Pin 12 (GPIO 18)  
DHT22 Pin 4 (GND) ──[Schwarz]──→ Pi5 Pin 39 (GND)
+ 10kΩ Pull-up zwischen DATA und VDD
```

### 🧪 AKTUELLE VERKABELUNG TESTEN:
Deine Verkabelung **kann trotzdem funktionieren**, teste sie erst:
```bash
cd /home/pi/Heizung_auslesen

# Virtual Environment aktivieren
source heizung_venv/bin/activate

# DHT22 Test mit deiner Verkabelung
python3 scripts/test_dht22_safe.py
```

Falls Probleme auftreten:
1. **GPIO 17 auf HIGH setzen** (für Stromversorgung)
2. **Oder umstecken auf Pin 1 (3.3V)**

## 💡 Pro-Tipp:

Falls GPIO 18 Probleme macht, alternative Pins:
- GPIO 17 (Pin 11) - oft bessere Library-Unterstützung
- GPIO 22 (Pin 15) - alternative Option
- GPIO 23 (Pin 16) - weitere Alternative

Dann im Code die Zeile ändern:
```python
# In scripts/test_dht22_*.py
gpio_pin = 17  # statt 18
```

---
🏠📊 **Happy Wiring!**
