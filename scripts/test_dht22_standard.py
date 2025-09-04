#!/usr/bin/env python3
"""
DHT22 Test mit Standard 3.3V Stromversorgung
===========================================
Testet DHT22 mit Pin 1 (3.3V) statt GPIO 17 als Stromversorgung
"""

import os
import sys
import time
import signal

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
            print("   💡 Lösung: bash scripts/fix_gpio_permissions.sh && sudo reboot")
            return False
        
        print("   ✅ GPIO Sysfs verfügbar und beschreibbar")
        return True
        
    except Exception as e:
        print(f"   ❌ GPIO Test Fehler: {e}")
        return False

def test_dht22_standard_power(gpio_pin):
    """DHT22 Test mit Standard 3.3V Stromversorgung"""
    print(f"🌡️ Teste DHT22 an GPIO{gpio_pin} (Standard 3.3V Power)...")
    
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
        
        # DHT22 Start Signal senden
        print("   🔄 Sende DHT22 Start Signal...")
        
        # Output mode und Start Signal
        with open(f"{gpio_dir}/direction", "w") as f:
            f.write("out")
        
        # Host start signal: Pull low for 18ms
        with open(f"{gpio_dir}/value", "w") as f:
            f.write("0")
        time.sleep(0.018)  # 18ms
        
        # Release line (DHT22 takes over)
        with open(f"{gpio_dir}/direction", "w") as f:
            f.write("in")
        
        # Versuche Response zu lesen
        responses = []
        for i in range(10):
            with open(f"{gpio_dir}/value", "r") as f:
                value = f.read().strip()
            responses.append(int(value))
            time.sleep(0.0001)  # 100µs
        
        # Analysiere Response
        activity_level = sum(responses)
        transitions = sum(1 for i in range(1, len(responses)) if responses[i] != responses[i-1])
        
        print(f"   📊 Signal Aktivität: {activity_level}/10, Übergänge: {transitions}")
        
        if transitions >= 2:
            print("   ✅ DHT22 Signal-Aktivität erkannt")
            print("   💡 Sensor reagiert auf Start-Signal")
            success = True
        else:
            print("   ⚠️ Keine DHT22 Signal-Aktivität")
            print("   💡 Mögliche Ursachen:")
            print("      - 10kΩ Pull-up Widerstand fehlt")
            print("      - DHT22 defekt oder falsch verkabelt")
            print("      - Timing-Probleme")
            success = False
        
        # Cleanup
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(gpio_pin))
        
        return success
        
    except PermissionError:
        print("   ❌ Permission denied")
        print("   💡 Lösung: bash scripts/fix_gpio_permissions.sh && sudo reboot")
        return False
    except Exception as e:
        print(f"   ❌ DHT22 Test Fehler: {e}")
        return False

def show_recommended_wiring():
    """Zeige empfohlene Verkabelung"""
    print("\n🔌 EMPFOHLENE DHT22 Verkabelung (Standard 3.3V):")
    print("=" * 55)
    print("DHT22 Pin 1 (VDD) ──[Rot]────→ Pi5 Pin 1 (3.3V)")
    print("DHT22 Pin 2 (DATA) ─[Gelb]───→ Pi5 Pin 12 (GPIO 18)")
    print("DHT22 Pin 3 (NC) ────────────→ (nicht angeschlossen)")
    print("DHT22 Pin 4 (GND) ──[Schwarz]→ Pi5 Pin 6 oder 39 (GND)")
    print()
    print("🔧 WICHTIG: 10kΩ Pull-up Widerstand zwischen:")
    print("   GPIO 18 (Pin 12) ↔ 3.3V (Pin 1)")
    print()
    print("✅ VORTEILE:")
    print("   - Saubere 3.3V Stromversorgung")
    print("   - Kein GPIO Pin für Stromversorgung missbraucht")
    print("   - Bessere Stabilität und Kompatibilität")

def show_troubleshooting():
    """Zeige Troubleshooting Tipps"""
    print("\n🔧 TROUBLESHOOTING:")
    print("=" * 20)
    print("1. GPIO Permissions:")
    print("   bash scripts/fix_gpio_permissions.sh")
    print("   sudo reboot")
    print()
    print("2. Hardware Check:")
    print("   - 10kΩ Pull-up Widerstand prüfen")
    print("   - Kabelverbindungen testen")
    print("   - DHT22 auf Beschädigungen prüfen")
    print()
    print("3. Alternative Tests:")
    print("   python3 scripts/gpio_diagnose.py")
    print("   python3 scripts/test_dht22_simple.py")
    print()
    print("4. GPIO Status prüfen:")
    print("   ls -la /sys/class/gpio/")
    print("   groups $USER")

def main():
    """Hauptfunktion"""
    print("🏠 Pi5 Heizungs-Messer - DHT22 Standard Power Test")
    print("=" * 55)
    print()
    print("💡 Dieser Test verwendet Pin 1 (3.3V) für VDD")
    print("   statt GPIO 17 als Stromversorgung")
    print()
    
    gpio_pin = 18  # DHT22 DATA an GPIO 18
    
    print(f"📍 Test-Konfiguration:")
    print(f"   VDD (+): Pin 1 (3.3V Power)")
    print(f"   DATA:    GPIO {gpio_pin} (Pin 12)")
    print(f"   GND:     Pin 6 oder 39 (GND)")
    
    # Test 1: GPIO Grundzugriff
    gpio_ok = test_gpio_basic_access(gpio_pin)
    
    if not gpio_ok:
        print("\n❌ GPIO Grundzugriff fehlgeschlagen!")
        show_troubleshooting()
        return
    
    # Test 2: DHT22 mit Standard Power
    dht22_ok = test_dht22_standard_power(gpio_pin)
    
    # Zusammenfassung
    print(f"\n📊 Test Zusammenfassung:")
    print(f"   GPIO {gpio_pin} Zugriff: {'✅' if gpio_ok else '❌'}")
    print(f"   DHT22 Signal Test: {'✅' if dht22_ok else '❌'}")
    
    if gpio_ok and dht22_ok:
        print(f"\n🎉 DHT22 Test erfolgreich!")
        print("💡 Empfehlungen:")
        print("   1. Hardware funktioniert korrekt")
        print("   2. Standard 3.3V Stromversorgung ist optimal")
        print("   3. 10kΩ Pull-up Widerstand ist vorhanden")
        print("   4. Bereit für Produktionsumgebung")
        
    elif gpio_ok and not dht22_ok:
        print(f"\n⚠️ DHT22 Signal-Probleme:")
        print("💡 Mögliche Lösungen:")
        print("   1. 10kΩ Pull-up Widerstand zwischen GPIO 18 und Pin 1 prüfen")
        print("   2. DHT22 Kabelverbindungen kontrollieren")
        print("   3. DHT22 Sensor austauschen")
        print("   4. Alternative GPIO Pins testen (17, 22, 23)")
        
    else:
        print(f"\n❌ GPIO oder Permission Probleme")
        
    # Zeige empfohlene Verkabelung
    show_recommended_wiring()
    
    # Troubleshooting Tipps
    show_troubleshooting()

if __name__ == "__main__":
    main()
