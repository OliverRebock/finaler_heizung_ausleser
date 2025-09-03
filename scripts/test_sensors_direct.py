#!/usr/bin/env python3
"""
Pi5 Heizungs Messer - Verbesserte Sensor Test Script
====================================================

Test-Script das direkt mit /sys/bus/w1/devices arbeitet.
"""

import os
import sys
import time
import glob
from pathlib import Path

print("🏠 Pi5 Heizungs Messer - Hardware Test")
print("=" * 50)

def test_w1_interface():
    """1-Wire Interface direkt testen"""
    print("\n🔌 1-Wire Interface Test:")
    
    w1_path = "/sys/bus/w1/devices/"
    if not os.path.exists(w1_path):
        print("❌ 1-Wire Interface nicht verfügbar")
        print("   Pfad nicht gefunden:", w1_path)
        return False
    
    print("✅ 1-Wire Interface verfügbar")
    
    # Alle Devices auflisten
    try:
        devices = os.listdir(w1_path)
        print(f"📋 Gefundene W1-Devices: {len(devices)}")
        for device in sorted(devices):
            print(f"   - {device}")
        
        # DS18B20 Sensoren filtern (beginnen mit "28-")
        ds18b20_devices = [d for d in devices if d.startswith("28-")]
        print(f"\n🌡️ DS18B20 Sensoren gefunden: {len(ds18b20_devices)}")
        
        return ds18b20_devices
        
    except Exception as e:
        print(f"❌ Fehler beim Lesen der W1-Devices: {e}")
        return False

def read_ds18b20_direct(sensor_id):
    """DS18B20 direkt über Filesystem lesen"""
    try:
        device_file = f"/sys/bus/w1/devices/{sensor_id}/w1_slave"
        
        if not os.path.exists(device_file):
            return None, f"Device-File nicht gefunden: {device_file}"
        
        # File lesen
        with open(device_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            return None, "Unvollständige Daten"
        
        # CRC prüfen
        if "YES" not in lines[0]:
            return None, "CRC Fehler"
        
        # Temperatur extrahieren
        temp_line = lines[1]
        temp_pos = temp_line.find('t=')
        if temp_pos == -1:
            return None, "Temperatur-Token nicht gefunden"
        
        temp_string = temp_line[temp_pos + 2:]
        temp_celsius = float(temp_string) / 1000.0
        
        return temp_celsius, "OK"
        
    except Exception as e:
        return None, f"Exception: {e}"

def test_all_ds18b20_sensors():
    """Alle DS18B20 Sensoren testen"""
    print("\n🌡️ DS18B20 Sensoren Test:")
    print("-" * 40)
    
    # W1 Interface testen
    ds18b20_devices = test_w1_interface()
    
    if not ds18b20_devices:
        print("❌ Keine DS18B20 Sensoren gefunden!")
        return False
    
    print(f"\n📊 Teste {len(ds18b20_devices)} Sensoren:")
    
    success_count = 0
    for sensor_id in ds18b20_devices:
        print(f"\n🔍 Sensor: {sensor_id}")
        
        # 3 Versuche pro Sensor
        for attempt in range(3):
            temp, status = read_ds18b20_direct(sensor_id)
            
            if temp is not None:
                print(f"   ✅ Temperatur: {temp:.2f}°C")
                success_count += 1
                break
            else:
                print(f"   ⚠️ Versuch {attempt + 1}: {status}")
                if attempt < 2:
                    time.sleep(1)
        else:
            print(f"   ❌ Sensor {sensor_id} antwortet nicht")
    
    print(f"\n📈 Ergebnis: {success_count}/{len(ds18b20_devices)} Sensoren erfolgreich")
    return success_count > 0

def test_dht22_fallback():
    """DHT22 mit Fallback-Methoden testen"""
    print("\n🌡️💧 DHT22 Sensor Test:")
    print("-" * 30)
    
    try:
        # Versuche verschiedene DHT22 Libraries
        gpio_pin = 4  # Standard GPIO Pin
        
        # Methode 1: Adafruit CircuitPython
        try:
            import board
            import adafruit_dht
            
            dht = adafruit_dht.DHT22(getattr(board, f'D{gpio_pin}'))
            
            for attempt in range(5):
                try:
                    temperature = dht.temperature
                    humidity = dht.humidity
                    
                    if temperature is not None and humidity is not None:
                        print(f"   ✅ Adafruit DHT22: {temperature:.1f}°C, {humidity:.1f}% rH")
                        return True
                except RuntimeError as e:
                    if attempt < 4:
                        time.sleep(2)
                    continue
            
        except ImportError:
            print("   ⚠️ Adafruit CircuitPython DHT nicht verfügbar")
        except Exception as e:
            print(f"   ❌ Adafruit DHT22 Fehler: {e}")
        
        # Methode 2: RPi.GPIO mit DHT Implementation
        try:
            print("   🔄 Teste alternative DHT22 Implementierung...")
            # Placeholder für alternative DHT22 Implementierung
            print("   ⚠️ Alternative DHT22 Implementierung noch nicht verfügbar")
            
        except Exception as e:
            print(f"   ❌ Alternative DHT22 Fehler: {e}")
        
        print("   ❌ DHT22 Sensor nicht erreichbar")
        return False
        
    except Exception as e:
        print(f"   ❌ DHT22 Test Fehler: {e}")
        return False

def show_system_info():
    """System-Informationen anzeigen"""
    print("\n💻 System Information:")
    print("-" * 25)
    
    try:
        # Pi Model
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip('\x00')
        print(f"   Modell: {model}")
    except:
        print("   Modell: Unbekannt")
    
    try:
        # Kernel Module
        with open('/proc/modules', 'r') as f:
            modules = f.read()
        
        w1_gpio = "w1-gpio" in modules
        w1_therm = "w1-therm" in modules
        
        print(f"   w1-gpio Modul: {'✅' if w1_gpio else '❌'}")
        print(f"   w1-therm Modul: {'✅' if w1_therm else '❌'}")
        
    except:
        print("   Module: Status unbekannt")
    
    # GPIO Status
    try:
        gpio_path = "/sys/class/gpio"
        if os.path.exists(gpio_path):
            print(f"   GPIO Interface: ✅")
        else:
            print(f"   GPIO Interface: ❌")
    except:
        print("   GPIO Interface: Unbekannt")

def main():
    """Hauptfunktion"""
    show_system_info()
    
    # DS18B20 Test
    ds18b20_ok = test_all_ds18b20_sensors()
    
    # DHT22 Test
    dht22_ok = test_dht22_fallback()
    
    # Ergebnis
    print("\n" + "="*50)
    print("📊 TEST ZUSAMMENFASSUNG:")
    print(f"   DS18B20 Sensoren: {'✅' if ds18b20_ok else '❌'}")
    print(f"   DHT22 Sensor: {'✅' if dht22_ok else '❌'}")
    
    if ds18b20_ok:
        print("\n🎉 Mindestens ein Sensor funktioniert!")
        print("💡 Nächste Schritte:")
        print("   1. config.ini anpassen")
        print("   2. Docker Services starten: bash scripts/deploy_docker.sh")
        print("   3. Sensor Reader starten: python src/sensor_reader.py")
    else:
        print("\n⚠️ Keine funktionierenden Sensoren gefunden!")
        print("🔧 Troubleshooting:")
        print("   1. Hardware-Verkabelung prüfen")
        print("   2. 1-Wire Interface: sudo raspi-config")
        print("   3. System reboot nach 1-Wire Aktivierung")
        print("   4. Module laden: sudo modprobe w1-gpio w1-therm")

if __name__ == "__main__":
    main()
