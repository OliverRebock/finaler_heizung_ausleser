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

### 🔗 Raspberry Pi 5 Verbindungen:

| DHT22 Pin | Beschreibung | Pi5 Pin | Pi5 GPIO | Kabel Farbe |
|-----------|--------------|---------|----------|-------------|
| Pin 1     | VDD (3.3V)   | Pin 1   | 3.3V     | Rot         |
| Pin 2     | DATA         | Pin 12  | GPIO 18  | Gelb/Grün   |
| Pin 3     | NC           | -       | -        | (nicht verwendet) |
| Pin 4     | GND          | Pin 6   | GND      | Schwarz     |

### 🔧 Zusätzlich benötigt:
- **10kΩ Widerstand** zwischen Pin 2 (DATA) und Pin 1 (VDD) als Pull-up

## 📊 Raspberry Pi 5 GPIO Layout (Ausschnitt):

```
Pi5 GPIO Header (erste 2 Zeilen):
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │  5  │  6  │  7  │  8  │  9  │ 10  │
│3.3V │ 5V  │GPIO2│ 5V  │GPIO3│ GND │GPIO4│TX   │ GND │ RX  │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ 11  │ 12  │ 13  │ 14  │ 15  │ 16  │ 17  │ 18  │ 19  │ 20  │
│GPIO17│GPIO18│GPIO27│GND │GPIO22│GPIO23│3.3V │GPIO24│MOSI │ GND │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

## ⚡ Schritt-für-Schritt Verkabelung:

### 1. **Stromversorgung (VDD)**
```
DHT22 Pin 1 (VDD) ──[Rot]──→ Pi5 Pin 1 (3.3V)
```

### 2. **Datenleitung (DATA) mit Pull-up**
```
DHT22 Pin 2 (DATA) ──[Gelb]──→ Pi5 Pin 12 (GPIO 18)
                     │
                     └──[10kΩ]──→ Pi5 Pin 1 (3.3V)
```

### 3. **Masse (GND)**
```
DHT22 Pin 4 (GND) ──[Schwarz]──→ Pi5 Pin 6 (GND)
```

### 4. **Pin 3 nicht anschließen**
```
DHT22 Pin 3 (NC) = Not Connected (frei lassen)
```

## 🧪 Test der Verkabelung:

Nach der Verkabelung teste mit:
```bash
cd /home/pi/Heizung_auslesen
python3 scripts/test_dht22_safe.py
```

## 🚨 Häufige Fehler:

❌ **FALSCH: GPIO 17 (Pin 11) verwenden**
✅ **RICHTIG: GPIO 18 (Pin 12) verwenden**

❌ **FALSCH: 5V Spannung verwenden**  
✅ **RICHTIG: 3.3V Spannung verwenden**

❌ **FALSCH: Pull-up Widerstand vergessen**
✅ **RICHTIG: 10kΩ zwischen DATA und VDD**

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
