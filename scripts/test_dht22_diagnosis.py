#!/usr/bin/env python3
"""
DHT22 Test mit direktem GPIO Zugriff
====================================
Testet DHT22 ohne Adafruit Library Dependencies
"""

import os
import sys
import time
import subprocess

def test_gpio_access(gpio_pin):
    """Teste GPIO Zugriff direkt"""
    print(f"🔍 Teste GPIO{gpio_pin} Zugriff...")
    
    gpio_export = "/sys/class/gpio/export"
    gpio_unexport = "/sys/class/gpio/unexport"
    gpio_dir = f"/sys/class/gpio/gpio{gpio_pin}"
    
    try:
        # Prüfe ob GPIO exportiert werden kann
        if not os.path.exists(gpio_dir):
            print(f"   📤 Exportiere GPIO{gpio_pin}...")
            with open(gpio_export, 'w') as f:
                f.write(str(gpio_pin))
            time.sleep(0.1)
        
        if not os.path.exists(gpio_dir):
            print(f"   ❌ GPIO{gpio_pin} konnte nicht exportiert werden")
            return False
        
        print(f"   ✅ GPIO{gpio_pin} erfolgreich exportiert")
        
        # Versuche Direction zu setzen
        direction_file = f"{gpio_dir}/direction"
        if os.path.exists(direction_file):
            with open(direction_file, 'w') as f:
                f.write('in')
            print(f"   ✅ GPIO{gpio_pin} als Input konfiguriert")
        
        # GPIO wieder freigeben
        with open(gpio_unexport, 'w') as f:
            f.write(str(gpio_pin))
        print(f"   🧹 GPIO{gpio_pin} freigegeben")
        
        return True
        
    except PermissionError as e:
        print(f"   ❌ Permission Error: {e}")
        print(f"   💡 Lösung: sudo usermod -aG gpio $USER && sudo reboot")
        return False
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        return False

def test_dht22_with_system_tools(gpio_pin):
    """Teste DHT22 mit System-Tools"""
    print(f"🔧 Teste DHT22 mit System-Tools an GPIO{gpio_pin}...")
    
    # Prüfe ob pigpio verfügbar ist
    try:
        result = subprocess.run(['which', 'pigpiod'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ pigpio gefunden")
            
            # Starte pigpiod falls nicht läuft
            result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True)
            if result.returncode != 0:
                print("   🔄 Starte pigpiod...")
                subprocess.run(['sudo', 'pigpiod'], check=False)
                time.sleep(1)
            
            # Teste mit pigpio Python
            try:
                import pigpio
                pi = pigpio.pi()
                if pi.connected:
                    print("   ✅ pigpio Verbindung hergestellt")
                    pi.stop()
                    print("   ⚠️ DHT22 pigpio Implementierung noch nicht verfügbar")
                    return False
                else:
                    print("   ❌ pigpio Verbindung fehlgeschlagen")
                    return False
            except ImportError:
                print("   ⚠️ pigpio Python Library nicht installiert")
                print("   💡 Installation: sudo apt install python3-pigpio")
                return False
        else:
            print("   ⚠️ pigpio nicht gefunden")
            print("   💡 Installation: sudo apt install pigpio")
            return False
            
    except Exception as e:
        print(f"   ❌ System-Tools Test Fehler: {e}")
        return False

def test_dht22_alternative_methods(gpio_pin):
    """Teste DHT22 mit alternativen Methoden"""
    print(f"\n🌡️💧 DHT22 Alternative Test Methoden (GPIO{gpio_pin}):")
    print("-" * 50)
    
    # Test 1: GPIO Zugriff
    gpio_ok = test_gpio_access(gpio_pin)
    
    # Test 2: System Tools
    tools_ok = test_dht22_with_system_tools(gpio_pin)
    
    # Test 3: Adafruit Library (falls verfügbar)
    print(f"\n🔄 Teste Adafruit Library mit GPIO{gpio_pin}...")
    try:
        import board
        import adafruit_dht
        
        # Pin Mapping korrigieren
        pin_mapping = {
            4: board.D4,
            17: board.D17, 
            18: board.D18,
            22: board.D22,
            23: board.D23,
            24: board.D24,
            25: board.D25,
            27: board.D27
        }
        
        if gpio_pin not in pin_mapping:
            print(f"   ❌ GPIO{gpio_pin} nicht in Adafruit Pin-Mapping")
            print(f"   💡 Unterstützte Pins: {list(pin_mapping.keys())}")
            adafruit_ok = False
        else:
            board_pin = pin_mapping[gpio_pin]
            print(f"   📍 Verwende {board_pin} für GPIO{gpio_pin}")
            
            try:
                dht = adafruit_dht.DHT22(board_pin)
                
                print("   🔄 Teste DHT22 Sensor...")
                success = False
                
                for attempt in range(3):
                    try:
                        temp = dht.temperature
                        humidity = dht.humidity
                        
                        if temp is not None and humidity is not None:
                            print(f"   ✅ DHT22: {temp:.1f}°C, {humidity:.1f}% rH")
                            success = True
                            break
                    except RuntimeError as e:
                        print(f"   ⚠️ Versuch {attempt + 1}: {e}")
                        if "GPIO" in str(e) and ("input" in str(e) or "line" in str(e)):
                            print(f"   ❌ GPIO Permission/Mapping Fehler")
                            break
                        time.sleep(2)
                
                dht.exit()
                adafruit_ok = success
                
            except Exception as e:
                print(f"   ❌ Adafruit DHT22 Fehler: {e}")
                adafruit_ok = False
        
    except ImportError:
        print("   ⚠️ Adafruit CircuitPython DHT nicht verfügbar")
        adafruit_ok = False
    
    # Zusammenfassung
    print(f"\n📊 DHT22 Test Ergebnisse (GPIO{gpio_pin}):")
    print(f"   GPIO Zugriff: {'✅' if gpio_ok else '❌'}")
    print(f"   System Tools: {'✅' if tools_ok else '❌'}")
    print(f"   Adafruit Library: {'✅' if adafruit_ok else '❌'}")
    
    if not any([gpio_ok, tools_ok, adafruit_ok]):
        print(f"\n⚠️ DHT22 an GPIO{gpio_pin} nicht funktionsfähig")
        print("💡 Mögliche Lösungen:")
        print("   1. GPIO Permissions: bash scripts/fix_gpio_permissions.sh")
        print("   2. Neuanmeldung: sudo reboot")
        print("   3. Hardware prüfen: Verkabelung, Sensor")
        print("   4. Anderen GPIO Pin testen (17, 22, 23, 24, 25, 27)")
        print("   5. Temporär als sudo ausführen")
        return False
    else:
        print(f"\n✅ DHT22 an GPIO{gpio_pin} grundsätzlich erreichbar!")
        return True

def main():
    """Hauptfunktion"""
    print("🏠 Pi5 Heizungs-Messer - DHT22 Diagnose")
    print("=" * 45)
    
    # Standard GPIO Pin
    gpio_pin = 18
    
    # Test mit GPIO 18
    result = test_dht22_alternative_methods(gpio_pin)
    
    if not result:
        print(f"\n🔄 Teste alternative GPIO Pins...")
        alternative_pins = [17, 22, 23, 24, 25, 27]
        
        for pin in alternative_pins:
            print(f"\n📍 Teste GPIO{pin}...")
            if test_gpio_access(pin):
                print(f"✅ GPIO{pin} funktioniert!")
                print(f"💡 Erwäge DHT22 an GPIO{pin} anzuschließen")
                break
        else:
            print("\n❌ Keine funktionierenden GPIO Pins gefunden")
            print("🔧 System-Level Troubleshooting erforderlich")

if __name__ == "__main__":
    main()
