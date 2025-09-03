#!/usr/bin/env python3
"""
Pi5 Heizungs Messer - Hauptsensor Reader
=========================================

Zentrale Klasse für das Auslesen aller Sensoren und Datenverarbeitung.
Optimiert für Raspberry Pi 5 Hardware.

Autor: Pi5 Heizungs Messer Project
"""

import time
import logging
import configparser
import threading
from datetime import datetime
from typing import Dict, List, Optional
import os
import sys

# Hardware Module
from hardware.ds18b20_sensor import DS18B20Reader
from hardware.dht22_sensor import DHT22Reader

# Externe Dependencies (Optional)
try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False
    print("⚠️ InfluxDB Client nicht verfügbar - pip install influxdb-client")

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/pi/pi5-sensors/sensor_reader.log')
    ]
)
logger = logging.getLogger(__name__)


class Pi5SensorReader:
    """
    Hauptklasse für Pi5 Heizungsüberwachung
    Koordiniert alle Sensoren und Datenfluss
    """
    
    def __init__(self, config_file='config.ini'):
        """Initialisiere Sensor Reader"""
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Sensor Instanzen
        self.ds18b20_reader = None
        self.dht22_reader = None
        self.influx_client = None
        
        # Status Tracking
        self.running = False
        self.last_reading = None
        
        logger.info("🌡️ Pi5 Sensor Reader initialisiert")
        
        # Hardware initialisieren
        self._setup_sensors()
        self._setup_database()
    
    def _setup_sensors(self):
        """Hardware Sensoren einrichten"""
        try:
            # DS18B20 1-Wire Temperatursensoren
            if self.config.getboolean('hardware', 'ds18b20_enabled', fallback=True):
                self.ds18b20_reader = DS18B20Reader(self.config)
                logger.info("✅ DS18B20 Reader initialisiert")
            
            # DHT22 Temperatur/Luftfeuchtigkeit
            if self.config.getboolean('hardware', 'dht22_enabled', fallback=True):
                dht22_gpio = self.config.getint('hardware', 'dht22_gpio', fallback=17)
                self.dht22_reader = DHT22Reader(gpio_pin=dht22_gpio)
                logger.info("✅ DHT22 Reader initialisiert")
                
        except Exception as e:
            logger.error(f"❌ Sensor Setup Fehler: {e}")
    
    def _setup_database(self):
        """InfluxDB Verbindung einrichten"""
        if not INFLUXDB_AVAILABLE:
            logger.warning("⚠️ InfluxDB nicht verfügbar - Daten werden nur geloggt")
            return
            
        try:
            host = self.config.get('database', 'host', fallback='localhost')
            port = self.config.getint('database', 'port', fallback=8086)
            token = self.config.get('database', 'token', fallback='pi5-token-2024')
            org = self.config.get('database', 'org', fallback='pi5org')
            
            url = f"http://{host}:{port}"
            self.influx_client = InfluxDBClient(url=url, token=token, org=org)
            
            # Health Check
            health = self.influx_client.health()
            if health.status == "pass":
                logger.info("✅ InfluxDB Verbindung erfolgreich")
            else:
                logger.error(f"❌ InfluxDB Health Check fehlgeschlagen: {health.status}")
                
        except Exception as e:
            logger.error(f"❌ InfluxDB Setup Fehler: {e}")
            self.influx_client = None
    
    def read_all_sensors(self) -> Dict:
        """Alle Sensoren auslesen"""
        sensor_data = {
            'timestamp': datetime.now().isoformat(),
            'temperatures': {},
            'humidity': {},
            'status': 'ok'
        }
        
        try:
            # DS18B20 Temperatursensoren
            if self.ds18b20_reader:
                temperatures = self.ds18b20_reader.read_all_temperatures()
                sensor_data['temperatures'].update(temperatures)
                logger.info(f"📊 DS18B20: {len(temperatures)} Sensoren gelesen")
            
            # DHT22 Umgebungssensor
            if self.dht22_reader:
                dht_data = self.dht22_reader.read_sensor()
                if dht_data:
                    sensor_data['temperatures']['dht22'] = dht_data['temperature']
                    sensor_data['humidity']['dht22'] = dht_data['humidity']
                    logger.info(f"📊 DHT22: {dht_data['temperature']:.1f}°C, {dht_data['humidity']:.1f}%")
            
            self.last_reading = sensor_data
            
        except Exception as e:
            logger.error(f"❌ Sensor Lese-Fehler: {e}")
            sensor_data['status'] = 'error'
            sensor_data['error'] = str(e)
        
        return sensor_data
    
    def save_to_influxdb(self, sensor_data: Dict):
        """Sensordaten in InfluxDB speichern"""
        if not self.influx_client:
            return False
            
        try:
            write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            bucket = self.config.get('database', 'bucket', fallback='sensors')
            points = []
            
            # Temperaturen schreiben
            for sensor_id, temperature in sensor_data['temperatures'].items():
                if temperature is not None:
                    # Sensor Namen aus Config laden
                    sensor_name = self.config.get('labels', sensor_id, fallback=sensor_id)
                    
                    point = Point("temperature") \
                        .tag("sensor_id", sensor_id) \
                        .tag("name", sensor_name) \
                        .field("value", float(temperature)) \
                        .time(datetime.now())
                    points.append(point)
            
            # Luftfeuchtigkeit schreiben
            for sensor_id, humidity in sensor_data['humidity'].items():
                if humidity is not None:
                    sensor_name = self.config.get('labels', sensor_id, fallback=sensor_id)
                    
                    point = Point("humidity") \
                        .tag("sensor_id", sensor_id) \
                        .tag("name", sensor_name) \
                        .field("value", float(humidity)) \
                        .time(datetime.now())
                    points.append(point)
            
            # Daten schreiben
            if points:
                write_api.write(bucket=bucket, record=points)
                logger.info(f"💾 {len(points)} Datenpunkte in InfluxDB gespeichert")
                return True
            
        except Exception as e:
            logger.error(f"❌ InfluxDB Schreibfehler: {e}")
            return False
        
        return False
    
    def run_once(self):
        """Einmalige Sensor-Ablesung"""
        logger.info("🔄 Einmalige Sensor-Ablesung...")
        
        sensor_data = self.read_all_sensors()
        
        # Daten in InfluxDB speichern
        if sensor_data['status'] == 'ok':
            self.save_to_influxdb(sensor_data)
        
        # Daten ausgeben
        self._print_sensor_summary(sensor_data)
        
        return sensor_data
    
    def run_continuous(self, interval: int = 30):
        """Kontinuierliche Sensor-Ablesung"""
        logger.info(f"🔄 Starte kontinuierliche Ablesung (alle {interval}s)")
        self.running = True
        
        try:
            while self.running:
                sensor_data = self.read_all_sensors()
                
                if sensor_data['status'] == 'ok':
                    self.save_to_influxdb(sensor_data)
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("👋 Sensor Reader beendet durch Benutzer")
        except Exception as e:
            logger.error(f"❌ Fehler in kontinuierlicher Schleife: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Sensor Reader beenden"""
        self.running = False
        if self.influx_client:
            self.influx_client.close()
        logger.info("🛑 Sensor Reader gestoppt")
    
    def _print_sensor_summary(self, sensor_data: Dict):
        """Sensor-Zusammenfassung ausgeben"""
        print("\n" + "="*50)
        print(f"📊 SENSOR ABLESUNG - {sensor_data['timestamp']}")
        print("="*50)
        
        # Temperaturen
        if sensor_data['temperatures']:
            print("\n🌡️ TEMPERATUREN:")
            for sensor_id, temp in sensor_data['temperatures'].items():
                if temp is not None:
                    sensor_name = self.config.get('labels', sensor_id, fallback=sensor_id)
                    print(f"   {sensor_name}: {temp:.1f}°C")
                else:
                    print(f"   {sensor_id}: Fehler")
        
        # Luftfeuchtigkeit
        if sensor_data['humidity']:
            print("\n💧 LUFTFEUCHTIGKEIT:")
            for sensor_id, humidity in sensor_data['humidity'].items():
                if humidity is not None:
                    sensor_name = self.config.get('labels', sensor_id, fallback=sensor_id)
                    print(f"   {sensor_name}: {humidity:.1f}%")
        
        print("\n" + "="*50)
    
    def get_sensor_status(self) -> Dict:
        """Aktuellen Sensor-Status zurückgeben"""
        status = {
            'sensors': {
                'ds18b20': self.ds18b20_reader is not None,
                'dht22': self.dht22_reader is not None
            },
            'database': self.influx_client is not None,
            'last_reading': self.last_reading,
            'running': self.running
        }
        
        if self.ds18b20_reader:
            status['sensors']['ds18b20_count'] = len(self.ds18b20_reader.get_sensor_ids())
        
        return status


def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pi5 Heizungs Messer - Sensor Reader')
    parser.add_argument('--config', default='config.ini', help='Konfigurationsdatei')
    parser.add_argument('--once', action='store_true', help='Einmalige Ablesung')
    parser.add_argument('--interval', type=int, default=30, help='Ablesung-Intervall in Sekunden')
    parser.add_argument('--test', action='store_true', help='Test-Modus')
    
    args = parser.parse_args()
    
    try:
        # Sensor Reader initialisieren
        reader = Pi5SensorReader(config_file=args.config)
        
        if args.test:
            print("🧪 Test-Modus: Sensor Status prüfen")
            status = reader.get_sensor_status()
            print(f"Sensors: {status['sensors']}")
            print(f"Database: {status['database']}")
            
        elif args.once:
            reader.run_once()
        else:
            reader.run_continuous(interval=args.interval)
            
    except KeyboardInterrupt:
        logger.info("👋 Programm beendet")
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
