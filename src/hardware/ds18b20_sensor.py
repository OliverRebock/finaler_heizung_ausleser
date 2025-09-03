#!/usr/bin/env python3
"""
DS18B20 1-Wire Temperatursensor Reader für Pi5
===============================================

Klasse für das Auslesen von DS18B20 Temperatursensoren über das
1-Wire Interface des Raspberry Pi 5.

Autor: Pi5 Heizungs Messer Project
"""

import os
import time
import logging
from typing import Dict, List, Optional
import configparser

logger = logging.getLogger(__name__)


class DS18B20Reader:
    """
    DS18B20 1-Wire Temperatursensor Reader
    Optimiert für Raspberry Pi 5 Hardware
    """
    
    def __init__(self, config: configparser.ConfigParser = None):
        """Initialisiere DS18B20 Reader"""
        self.config = config
        self.w1_device_path = "/sys/bus/w1/devices/"
        self.sensor_ids = []
        
        # 1-Wire Interface prüfen
        if not self._check_w1_interface():
            logger.warning("⚠️ 1-Wire Interface nicht verfügbar")
        else:
            self._discover_sensors()
    
    def _check_w1_interface(self) -> bool:
        """1-Wire Interface verfügbarkeit prüfen"""
        try:
            # Prüfe ob 1-Wire aktiviert ist
            w1_masters = "/sys/bus/w1/devices/w1_bus_master1"
            if not os.path.exists(w1_masters):
                logger.error("❌ 1-Wire Interface nicht aktiviert!")
                logger.error("   Aktiviere mit: sudo raspi-config → Interface Options → 1-Wire")
                return False
            
            # Prüfe Device Directory
            if not os.path.exists(self.w1_device_path):
                logger.error(f"❌ 1-Wire Device Path nicht gefunden: {self.w1_device_path}")
                return False
            
            logger.info("✅ 1-Wire Interface verfügbar")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler bei 1-Wire Interface Prüfung: {e}")
            return False
    
    def _discover_sensors(self):
        """Automatische Sensor-Erkennung"""
        try:
            if not os.path.exists(self.w1_device_path):
                logger.warning(f"W1 Device Path nicht gefunden: {self.w1_device_path}")
                return
            
            # Alle DS18B20 Sensoren finden (beginnen mit "28-")
            devices = os.listdir(self.w1_device_path)
            ds18b20_sensors = [d for d in devices if d.startswith("28-")]
            
            logger.info(f"🔍 Gefundene W1-Devices: {devices}")
            logger.info(f"🌡️ DS18B20 Sensoren erkannt: {ds18b20_sensors}")
            
            # Konfigurierte Sensoren verwenden falls vorhanden
            if (self.config and 
                self.config.has_section('hardware') and 
                self.config.has_option('hardware', 'ds18b20_sensors') and
                self.config.get('hardware', 'ds18b20_sensors').strip()):
                
                configured_sensors = self.config.get('hardware', 'ds18b20_sensors').split(',')
                configured_sensors = [s.strip() for s in configured_sensors if s.strip()]
                
                logger.info(f"🔧 Konfigurierte Sensoren: {configured_sensors}")
                
                # Nur konfigurierte Sensoren verwenden die auch physisch vorhanden sind
                self.sensor_ids = [s for s in configured_sensors if s in ds18b20_sensors]
                
                if len(self.sensor_ids) != len(configured_sensors):
                    missing = set(configured_sensors) - set(self.sensor_ids)
                    logger.warning(f"⚠️ Konfigurierte Sensoren nicht gefunden: {missing}")
                    
                logger.info(f"✅ Verwende konfigurierte Sensoren: {self.sensor_ids}")
            else:
                # Alle gefundenen Sensoren verwenden (Auto-Discovery)
                self.sensor_ids = ds18b20_sensors
                logger.info(f"🔍 Auto-Discovery: Verwende alle gefundenen Sensoren")
            
            logger.info(f"📊 {len(self.sensor_ids)} DS18B20 Sensoren werden verwendet: {self.sensor_ids}")
            
            # Sensor Tests
            for sensor_id in self.sensor_ids:
                temp = self.read_temperature(sensor_id)
                if temp is not None:
                    logger.info(f"   ✅ {sensor_id}: {temp:.1f}°C")
                else:
                    logger.warning(f"   ❌ {sensor_id}: Lesefehler")
                    
        except Exception as e:
            logger.error(f"❌ Fehler bei Sensor-Erkennung: {e}")
            logger.error(f"   Prüfe 1-Wire Interface und Sensor-Verkabelung")
    
    def read_temperature(self, sensor_id: str) -> Optional[float]:
        """Temperatur von spezifischem Sensor lesen"""
        try:
            sensor_file = f"{self.w1_device_path}{sensor_id}/w1_slave"
            
            if not os.path.exists(sensor_file):
                logger.error(f"❌ Sensor-Datei nicht gefunden: {sensor_file}")
                return None
            
            # Sensor-Datei lesen
            with open(sensor_file, 'r') as f:
                content = f.read()
            
            # Daten validieren
            lines = content.strip().split('\n')
            if len(lines) < 2:
                logger.error(f"❌ Ungültige Sensor-Daten für {sensor_id}")
                return None
            
            # CRC prüfen
            if 'YES' not in lines[0]:
                logger.warning(f"⚠️ CRC Fehler bei Sensor {sensor_id}")
                return None
            
            # Temperatur extrahieren
            temp_line = lines[1]
            temp_start = temp_line.find('t=')
            if temp_start == -1:
                logger.error(f"❌ Temperatur-Wert nicht gefunden für {sensor_id}")
                return None
            
            temp_string = temp_line[temp_start + 2:]
            temp_celsius = float(temp_string) / 1000.0
            
            # Plausibilitätsprüfung
            if temp_celsius < -55 or temp_celsius > 125:
                logger.warning(f"⚠️ Temperatur außerhalb des Bereichs: {temp_celsius}°C")
                return None
            
            return round(temp_celsius, 2)
            
        except FileNotFoundError:
            logger.error(f"❌ Sensor {sensor_id} nicht gefunden")
            return None
        except ValueError as e:
            logger.error(f"❌ Temperatur-Parsing Fehler für {sensor_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler beim Lesen von {sensor_id}: {e}")
            return None
    
    def read_temperature_with_retry(self, sensor_id: str, max_retries: int = 3) -> Optional[float]:
        """Temperatur mit Wiederholungsversuchen lesen"""
        for attempt in range(max_retries):
            temp = self.read_temperature(sensor_id)
            if temp is not None:
                return temp
            
            if attempt < max_retries - 1:
                logger.warning(f"⚠️ Leseversuch {attempt + 1} fehlgeschlagen für {sensor_id}, wiederhole...")
                time.sleep(0.1)  # Kurze Pause zwischen Versuchen
        
        logger.error(f"❌ Alle {max_retries} Leseversuche für {sensor_id} fehlgeschlagen")
        return None
    
    def read_all_temperatures(self) -> Dict[str, float]:
        """Alle verfügbaren Sensoren auslesen"""
        temperatures = {}
        
        for sensor_id in self.sensor_ids:
            temp = self.read_temperature_with_retry(sensor_id)
            if temp is not None:
                temperatures[sensor_id] = temp
            else:
                logger.warning(f"⚠️ Sensor {sensor_id} konnte nicht gelesen werden")
                temperatures[sensor_id] = None
        
        return temperatures
    
    def get_sensor_ids(self) -> List[str]:
        """Liste aller verfügbaren Sensor-IDs zurückgeben"""
        return self.sensor_ids.copy()
    
    def get_sensor_count(self) -> int:
        """Anzahl verfügbarer Sensoren zurückgeben"""
        return len(self.sensor_ids)
    
    def is_sensor_available(self, sensor_id: str) -> bool:
        """Prüfen ob spezifischer Sensor verfügbar ist"""
        return sensor_id in self.sensor_ids
    
    def test_all_sensors(self) -> Dict[str, bool]:
        """Alle Sensoren testen"""
        test_results = {}
        
        logger.info("🧪 Teste alle DS18B20 Sensoren...")
        
        for sensor_id in self.sensor_ids:
            temp = self.read_temperature(sensor_id)
            test_results[sensor_id] = temp is not None
            
            if temp is not None:
                logger.info(f"   ✅ {sensor_id}: {temp:.1f}°C")
            else:
                logger.error(f"   ❌ {sensor_id}: Fehler")
        
        working_count = sum(test_results.values())
        total_count = len(test_results)
        
        logger.info(f"📊 DS18B20 Test Ergebnis: {working_count}/{total_count} Sensoren funktional")
        
        return test_results


def main():
    """Test-Funktion für DS18B20 Reader"""
    import argparse
    
    # Logging für Tests
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = argparse.ArgumentParser(description='DS18B20 Sensor Test')
    parser.add_argument('--sensor', help='Spezifischen Sensor testen')
    parser.add_argument('--list', action='store_true', help='Alle verfügbaren Sensoren auflisten')
    parser.add_argument('--test', action='store_true', help='Alle Sensoren testen')
    
    args = parser.parse_args()
    
    # DS18B20 Reader initialisieren
    reader = DS18B20Reader()
    
    if args.list:
        print("\n📊 Verfügbare DS18B20 Sensoren:")
        for sensor_id in reader.get_sensor_ids():
            print(f"   {sensor_id}")
        print(f"\nGesamt: {reader.get_sensor_count()} Sensoren")
        
    elif args.sensor:
        print(f"\n🌡️ Teste Sensor {args.sensor}:")
        if reader.is_sensor_available(args.sensor):
            temp = reader.read_temperature_with_retry(args.sensor)
            if temp is not None:
                print(f"   Temperatur: {temp:.1f}°C")
            else:
                print("   ❌ Lesefehler")
        else:
            print("   ❌ Sensor nicht verfügbar")
            
    elif args.test:
        reader.test_all_sensors()
        
    else:
        # Standard: Alle Temperaturen einmal lesen
        print("\n🌡️ Lese alle DS18B20 Temperaturen:")
        temperatures = reader.read_all_temperatures()
        
        for sensor_id, temp in temperatures.items():
            if temp is not None:
                print(f"   {sensor_id}: {temp:.1f}°C")
            else:
                print(f"   {sensor_id}: Fehler")


if __name__ == "__main__":
    main()
