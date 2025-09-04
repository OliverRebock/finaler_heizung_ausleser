#!/usr/bin/env python3
"""
GPIO Status Checker
===================
Prüft GPIO Status und Permissions für DHT22 Debugging
"""

import os
import subprocess

def check_gpio_status():
    """Prüfe GPIO Status und bereits exportierte Pins"""
    print("🔍 GPIO Status Check")
    print("=" * 30)
    
    gpio_base = "/sys/class/gpio"
    
    # Prüfe GPIO Sysfs
    if not os.path.exists(gpio_base):
        print("❌ GPIO Sysfs nicht verfügbar")
        return False
    
    print("✅ GPIO Sysfs verfügbar")
    
    # Zeige bereits exportierte GPIOs
    try:
        exported_gpios = []
        for item in os.listdir(gpio_base):
            if item.startswith("gpio"):
                gpio_num = item.replace("gpio", "")
                if gpio_num.isdigit():
                    exported_gpios.append(gpio_num)
        
        if exported_gpios:
            print(f"📌 Bereits exportierte GPIOs: {', '.join(sorted(exported_gpios))}")
        else:
            print("📌 Keine GPIOs exportiert")
            
    except Exception as e:
        print(f"⚠️ Fehler beim Lesen exportierter GPIOs: {e}")
    
    # Prüfe Permissions
    export_file = f"{gpio_base}/export"
    unexport_file = f"{gpio_base}/unexport"
    
    print(f"\n🔑 Permission Check:")
    print(f"   export writeable: {'✅' if os.access(export_file, os.W_OK) else '❌'}")
    print(f"   unexport writeable: {'✅' if os.access(unexport_file, os.W_OK) else '❌'}")
    
    return True

def check_specific_gpio(gpio_num):
    """Prüfe spezifischen GPIO Pin"""
    print(f"\n🔍 GPIO {gpio_num} Detail Check:")
    
    gpio_dir = f"/sys/class/gpio/gpio{gpio_num}"
    
    if os.path.exists(gpio_dir):
        print(f"   ⚠️ GPIO {gpio_num} bereits exportiert")
        
        # Prüfe aktuelle Konfiguration
        try:
            with open(f"{gpio_dir}/direction", "r") as f:
                direction = f.read().strip()
            print(f"   📍 Direction: {direction}")
            
            if direction == "out":
                with open(f"{gpio_dir}/value", "r") as f:
                    value = f.read().strip()
                print(f"   📍 Value: {value}")
            
            # Prüfe wer den Pin verwendet
            try:
                result = subprocess.run(['lsof', gpio_dir], capture_output=True, text=True)
                if result.stdout.strip():
                    print(f"   ⚠️ Pin wird verwendet von:")
                    print(f"      {result.stdout.strip()}")
                else:
                    print(f"   ✅ Pin nicht aktiv verwendet")
            except:
                print(f"   ℹ️ lsof nicht verfügbar")
                
        except Exception as e:
            print(f"   ❌ Fehler beim Lesen: {e}")
            
        return "exported"
    else:
        print(f"   ✅ GPIO {gpio_num} nicht exportiert (verfügbar)")
        return "available"

def cleanup_gpio(gpio_num):
    """GPIO Pin freigeben"""
    print(f"\n🧹 Cleanup GPIO {gpio_num}:")
    
    gpio_dir = f"/sys/class/gpio/gpio{gpio_num}"
    
    if os.path.exists(gpio_dir):
        try:
            with open("/sys/class/gpio/unexport", "w") as f:
                f.write(str(gpio_num))
            print(f"   ✅ GPIO {gpio_num} freigegeben")
            return True
        except Exception as e:
            print(f"   ❌ Cleanup Fehler: {e}")
            return False
    else:
        print(f"   ℹ️ GPIO {gpio_num} war nicht exportiert")
        return True

def check_gpio_groups():
    """Prüfe GPIO Gruppen-Mitgliedschaft"""
    print(f"\n👥 Benutzer GPIO Gruppen:")
    
    try:
        # Aktuelle Gruppen
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout.strip()
        print(f"   Aktuelle Gruppen: {groups}")
        
        if 'gpio' in groups:
            print("   ✅ Benutzer in GPIO Gruppe")
        else:
            print("   ❌ Benutzer NICHT in GPIO Gruppe")
            print("   💡 Lösung: sudo usermod -aG gpio $USER && sudo reboot")
            
    except Exception as e:
        print(f"   ⚠️ Gruppen-Check Fehler: {e}")

def suggest_fixes():
    """Lösungsvorschläge anzeigen"""
    print(f"\n🔧 Lösungsvorschläge:")
    print("1. GPIO Permissions fix:")
    print("   bash scripts/fix_gpio_permissions.sh")
    print("   sudo reboot")
    print()
    print("2. Manuelle GPIO Freigabe:")
    print("   sudo su")
    print("   echo 17 > /sys/class/gpio/unexport")
    print("   echo 18 > /sys/class/gpio/unexport")
    print("   exit")
    print()
    print("3. Alternative: DHT22 auf Pin 1 (3.3V) umstecken:")
    print("   VDD: Pin 11 (GPIO 17) → Pin 1 (3.3V)")
    print("   Dann GPIO 17 nicht als Power verwenden")

def main():
    """Hauptfunktion"""
    print("🏠 Pi5 Heizungs-Messer - GPIO Diagnose")
    print("=" * 45)
    
    # Allgemeiner GPIO Status
    check_gpio_status()
    
    # Spezifische GPIOs prüfen  
    gpio17_status = check_specific_gpio(17)
    gpio18_status = check_specific_gpio(18)
    
    # GPIO Gruppen prüfen
    check_gpio_groups()
    
    # Cleanup anbieten wenn nötig
    if gpio17_status == "exported" or gpio18_status == "exported":
        print(f"\n🤔 GPIO Cleanup versuchen? (y/n): ", end="")
        try:
            response = input().lower()
            if response == 'y':
                if gpio17_status == "exported":
                    cleanup_gpio(17)
                if gpio18_status == "exported":
                    cleanup_gpio(18)
                print("\n✅ Cleanup abgeschlossen. Jetzt DHT22 Test wiederholen.")
        except KeyboardInterrupt:
            print("\nAbgebrochen.")
    
    # Lösungsvorschläge
    suggest_fixes()

if __name__ == "__main__":
    main()
