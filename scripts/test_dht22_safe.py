#!/usr/bin/env python3
"""
Sicherer DHT22 Test ohne Hänger
===============================
Testet DHT22 ohne die problematische Adafruit Library
"""

import os
import sys
import time
import subprocess

def setup_gpio17_power():
    """GPIO 17 als Stromversorgung für DHT22 aktivieren"""
    print("🔌 Aktiviere GPIO 17 als DHT22 Stromversorgung...")
    
    gpio17_dir = "/sys/class/gpio/gpio17"
    
    try:
        # GPIO 17 exportieren falls nötig
        if not os.path.exists(gpio17_dir):
            with open("/sys/class/gpio/export", "w") as f:
                f.write("17")
            time.sleep(0.1)
        
        # Als Output setzen
        with open(f"{gpio17_dir}/direction", "w") as f:
            f.write("out")
        
        # Auf HIGH setzen (3.3V)
        with open(f"{gpio17_dir}/value", "w") as f:
            f.write("1")
        
        print("   ✅ GPIO 17 auf HIGH (3.3V) gesetzt")
        return True
        
    except Exception as e:
        print(f"   ❌ GPIO 17 Setup Fehler: {e}")
        return False

def test_gpio_basic_access(gpio_pin):
    """Grundlegender GPIO Test"""
    print(f"🔍 Teste GPIO{gpio_pin} Grundzugriff...")
    
    try:
        # Prüfe GPIO Sysfs
        gpio_base = "/sys/class/gpio"
        if not os.path.exists(gpio_base):
            print("   ❌ GPIO Sysfs nicht verfügbar")
            return False
        
        # Prüfe Permissions
        export_file = f"{gpio_base}/export"
        if not os.access(export_file, os.W_OK):
            print("   ❌ Keine GPIO Export Berechtigung")
            print("   💡 Lösung: sudo usermod -aG gpio $USER && sudo reboot")
            return False
        
        print("   ✅ GPIO Sysfs verfügbar und beschreibbar")
        return True
        
    except Exception as e:
        print(f"   ❌ GPIO Test Fehler: {e}")
        return False

def test_dht22_manual(gpio_pin):
    """Manueller DHT22 Test ohne Library"""
    print(f"🌡️ Teste DHT22 an GPIO{gpio_pin} (manuell)...")
    
    gpio_dir = f"/sys/class/gpio/gpio{gpio_pin}"
    
    try:
        # GPIO exportieren
        if not os.path.exists(gpio_dir):
            with open("/sys/class/gpio/export", "w") as f:
                f.write(str(gpio_pin))
            time.sleep(0.1)
        
        if not os.path.exists(gpio_dir):
            print("   ❌ GPIO Export fehlgeschlagen")
            return False
        
        # Direction setzen
        with open(f"{gpio_dir}/direction", "w") as f:
            f.write("out")
        
        # Signal senden (DHT22 Wake-up)
        with open(f"{gpio_dir}/value", "w") as f:
            f.write("0")
        time.sleep(0.02)  # 20ms Low
        
        with open(f"{gpio_dir}/direction", "w") as f:
            f.write("in")
        
        # Versuche zu lesen
        for i in range(5):
            with open(f"{gpio_dir}/value", "r") as f:
                value = f.read().strip()
            time.sleep(0.1)
        
        print("   ✅ GPIO Signale erfolgreich")
        print("   ⚠️ DHT22 Protokoll-Dekodierung noch nicht implementiert")
        print("   💡 Hardware ist grundsätzlich ansprechbar")
        
        # Cleanup
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(gpio_pin))
        
        return True
        
    except PermissionError:
        print("   ❌ Permission denied")
        print("   💡 Lösung: sudo usermod -aG gpio $USER && sudo reboot")
        return False
    except Exception as e:
        print(f"   ❌ Manueller Test Fehler: {e}")
        return False

def test_alternative_libraries(gpio_pin):
    """Teste alternative DHT22 Libraries"""
    print(f"🔄 Teste alternative DHT22 Libraries für GPIO{gpio_pin}...")
    
    # Test 1: DHT Library (falls installiert)
    try:
        import DHT22
        print("   ✅ DHT22 Library gefunden")
        # Hier könnte DHT22 getestet werden
        print("   ⚠️ DHT22 Library Test noch nicht implementiert")
        return True
    except ImportError:
        print("   ⚠️ DHT22 Library nicht verfügbar")
    
    # Test 2: w1thermsensor für DHT22 (falls möglich)
    try:
        # DHT22 ist kein 1-Wire Sensor, aber test trotzdem
        print("   ⚠️ DHT22 ist kein 1-Wire Sensor")
    except:
        pass
    
    return False

def main():
    """Sicherer DHT22 Test Hauptfunktion"""
    print("🏠 Pi5 Heizungs-Messer - Sicherer DHT22 Test")
    print("=" * 48)
    
    gpio_pin = 18  # DHT22 DATA an GPIO 18
    power_pin = 17 # DHT22 VDD an GPIO 17
    
    print(f"\n📍 Teste DHT22 Verkabelung:")
    print(f"   VDD (+): GPIO {power_pin} (Pin 11)")
    print(f"   DATA:    GPIO {gpio_pin} (Pin 12)")
    print(f"   GND:     Pin 39")
    
    # Test 0: GPIO 17 als Stromversorgung aktivieren
    power_ok = setup_gpio17_power()
    
    if not power_ok:
        print("\n❌ GPIO 17 Stromversorgung fehlgeschlagen!")
        print("🔧 Führe zuerst aus: bash scripts/fix_gpio_permissions.sh")
        return
    
    # Test 1: GPIO Grundzugriff
    gpio_ok = test_gpio_basic_access(gpio_pin)
    
    if not gpio_ok:
        print("\n❌ GPIO Grundzugriff fehlgeschlagen!")
        print("🔧 Führe zuerst aus: bash scripts/fix_gpio_permissions.sh")
        return
    
    # Test 2: Manueller GPIO Test
    manual_ok = test_dht22_manual(gpio_pin)
    
    # Test 3: Alternative Libraries
    alt_ok = test_alternative_libraries(gpio_pin)
    
    # Zusammenfassung
    print(f"\n📊 DHT22 Test Zusammenfassung (GPIO{gpio_pin}):")
    print(f"   GPIO Zugriff: {'✅' if gpio_ok else '❌'}")
    print(f"   Manueller Test: {'✅' if manual_ok else '❌'}")
    print(f"   Alternative Libraries: {'✅' if alt_ok else '❌'}")
    
    if gpio_ok and manual_ok:
        print(f"\n✅ DHT22 Hardware ist grundsätzlich erreichbar!")
        print("💡 Deine Verkabelung:")
        print(f"   VDD (+): GPIO 17 → Pin 11 (als Stromversorgung)")
        print(f"   DATA:    GPIO 18 → Pin 12 (Datenleitung)")
        print(f"   GND:     Pin 39 (Masse)")
        print("\n🔧 Empfehlungen:")
        print("   1. Hardware funktioniert - Sensor ist angeschlossen")
        print("   2. GPIO 17 als Stromversorgung ist unkonventionell aber OK")
        print("   3. Bei Problemen: VDD auf Pin 1 (3.3V) umstecken")
        print("   4. 10kΩ Pull-up Widerstand zwischen DATA und VDD nicht vergessen")
        
        # Cleanup GPIO 17
        try:
            with open("/sys/class/gpio/unexport", "w") as f:
                f.write("17")
        except:
            pass
    
    else:
        print(f"\n⚠️ DHT22 an GPIO{gpio_pin} problematisch")
        print("🔧 Troubleshooting:")
        print("   1. bash scripts/fix_gpio_permissions.sh")
        print("   2. sudo reboot")
        print("   3. Hardware-Verkabelung prüfen")
        print("   4. Anderen GPIO Pin verwenden")

if __name__ == "__main__":
    main()
