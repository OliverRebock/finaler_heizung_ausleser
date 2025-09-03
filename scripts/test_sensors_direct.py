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
    
    gpio_pin = 18  # Standard GPIO Pin für DHT22
    
    # Prüfe GPIO Permissions
    print(f"🔍 Prüfe GPIO Pin {gpio_pin} Zugriff...")
    
    # GPIO Permission Test
    gpio_export_path = "/sys/class/gpio/export"
    gpio_pin_path = f"/sys/class/gpio/gpio{gpio_pin}"
    
    if not os.access(gpio_export_path, os.W_OK):
        print(f"❌ Keine GPIO Schreibberechtigung")
        print(f"   Lösung: sudo usermod -aG gpio $USER")
        print(f"   Oder Script als sudo ausführen")
        return False
    
    try:
        # Versuche verschiedene DHT22 Libraries
        
        # Methode 1: Adafruit CircuitPython (mit korrektem Pin-Mapping)
        try:
            print("   🔄 Teste Adafruit CircuitPython DHT...")
            import board
            import adafruit_dht
            
            # GPIO Pin Mapping für Raspberry Pi
            gpio_to_board_mapping = {
                4: board.D4,
                17: board.D17,
                18: board.D18,
                22: board.D22,
                23: board.D23,
                24: board.D24,
                25: board.D25,
                27: board.D27
            }
            
            if gpio_pin not in gpio_to_board_mapping:
                print(f"   ❌ GPIO{gpio_pin} nicht in Board-Mapping unterstützt")
                print(f"   💡 Unterstützte Pins: {list(gpio_to_board_mapping.keys())}")
                return False
            
            board_pin = gpio_to_board_mapping[gpio_pin]
            print(f"   📍 Verwende GPIO{gpio_pin} -> {board_pin}")
            
            # Timeout für DHT22 Test
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("DHT22 Test Timeout")
            
            # 10 Sekunden Timeout setzen
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)
            
            try:
                # Versuche DHT22 zu initialisieren
                dht = adafruit_dht.DHT22(board_pin)
                
                for attempt in range(3):
                    try:
                        print(f"   🔄 Messversuch {attempt + 1}/3...")
                        temperature = dht.temperature
                        humidity = dht.humidity
                        
                        if temperature is not None and humidity is not None:
                            print(f"   ✅ Adafruit DHT22: {temperature:.1f}°C, {humidity:.1f}% rH")
                            dht.exit()
                            signal.alarm(0)  # Timeout zurücksetzen
                            return True
                    except RuntimeError as e:
                        if "GPIO" in str(e) and ("input" in str(e) or "line" in str(e)):
                            print(f"   ❌ GPIO Permission/Pin Error: {e}")
                            print(f"   💡 Lösungen:")
                            print(f"      1. sudo usermod -aG gpio pi && sudo reboot")
                            print(f"      2. DHT22 an GPIO 17 anschließen (bessere Unterstützung)")
                            print(f"      3. Script als sudo ausführen")
                            dht.exit()
                            signal.alarm(0)
                            return False
                        elif "Checksum" in str(e) or "timeout" in str(e).lower():
                            print(f"   ⚠️ Versuch {attempt + 1}: Sensor-Timeout/Checksum")
                            if attempt < 2:
                                time.sleep(3)
                                continue
                        else:
                            print(f"   ⚠️ Versuch {attempt + 1}: {e}")
                            if attempt < 2:
                                time.sleep(3)
                                continue
                
                dht.exit()
                signal.alarm(0)
                print(f"   ❌ DHT22 antwortet nicht nach 3 Versuchen")
                
            except TimeoutError:
                print(f"   ❌ DHT22 Test Timeout (>10s) - wahrscheinlich Hardware-Problem")
                try:
                    dht.exit()
                except:
                    pass
                signal.alarm(0)
                return False
            except Exception as e:
                print(f"   ❌ DHT22 Initialisierung fehlgeschlagen: {e}")
                signal.alarm(0)
                return False
            finally:
                signal.alarm(0)  # Timeout immer zurücksetzen
            
        except ImportError:
            print("   ⚠️ Adafruit CircuitPython DHT nicht verfügbar")
        except Exception as e:
            print(f"   ❌ Adafruit DHT22 Fehler: {e}")
        
        # Methode 2: System-Tools Fallback
        try:
            print("   🔄 Teste System-Tools Alternative...")
            
            # Prüfe ob DHT-Tools installiert sind
            import subprocess
            result = subprocess.run(['which', 'dht22'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ System DHT-Tools gefunden")
                # Hier könnte DHT-Tool aufgerufen werden
                print("   ⚠️ System DHT-Tool Test noch nicht implementiert")
            else:
                print("   ⚠️ Keine System DHT-Tools gefunden")
                
        except Exception as e:
            print(f"   ❌ System-Tools Fehler: {e}")
        
        # Methode 3: GPIO Direct Access (nur für Test)
        try:
            print("   🔄 Teste direkten GPIO Zugriff...")
            
            # Test ob GPIO Pin exportiert werden kann
            if not os.path.exists(gpio_pin_path):
                with open(gpio_export_path, 'w') as f:
                    f.write(str(gpio_pin))
                print(f"   ✅ GPIO Pin {gpio_pin} exportiert")
                
                # Cleanup
                time.sleep(0.1)
                with open("/sys/class/gpio/unexport", 'w') as f:
                    f.write(str(gpio_pin))
                print(f"   🧹 GPIO Pin {gpio_pin} freigegeben")
            else:
                print(f"   ℹ️ GPIO Pin {gpio_pin} bereits exportiert")
            
            print("   ✅ GPIO Zugriff grundsätzlich möglich")
            print("   ⚠️ DHT22 Implementierung über direkten GPIO noch nicht verfügbar")
            
        except PermissionError:
            print(f"   ❌ GPIO Permission denied")
            print(f"   💡 Lösung: sudo usermod -aG gpio $USER && sudo reboot")
            return False
        except Exception as e:
            print(f"   ❌ GPIO Test Fehler: {e}")
        
        print("   ❌ DHT22 Sensor nicht erreichbar oder Permission-Problem")
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
        print("\n🎉 DS18B20 Sensoren funktionieren perfekt!")
        if not dht22_ok:
            print("\n⚠️ DHT22 Problem (GPIO Permissions):")
            print("💡 Lösungen:")
            print("   1. bash scripts/fix_gpio_permissions.sh")
            print("   2. sudo reboot")
            print("   3. Temporär: sudo python scripts/test_sensors_direct.py")
        
        print("\n💡 Nächste Schritte:")
        print("   1. config.ini anpassen (Sensor-IDs eintragen)")
        print("   2. Docker Services: bash scripts/deploy_docker.sh")
        print("   3. Sensor Reader: python src/sensor_reader.py")
    else:
        print("\n⚠️ Keine funktionierenden Sensoren gefunden!")
        print("🔧 Troubleshooting:")
        print("   1. Hardware-Verkabelung prüfen")
        print("   2. 1-Wire Interface: sudo raspi-config")
        print("   3. System reboot nach 1-Wire Aktivierung")
        print("   4. Module laden: sudo modprobe w1-gpio w1-therm")

if __name__ == "__main__":
    main()
