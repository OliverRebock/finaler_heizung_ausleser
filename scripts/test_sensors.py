#!/usr/bin/env python3
"""
Pi5 Heizungs Messer - Sensor Test Script
=========================================

Umfangreiches Test-Script für alle Sensoren und Komponenten.

Autor: Pi5 Heizungs Messer Project
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path

# Projekt Root zum Python Path hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from hardware.ds18b20_sensor import DS18B20Reader
from hardware.dht22_sensor import DHT22Reader
import configparser

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ds18b20_sensors(config=None):
    """DS18B20 Sensoren testen"""
    print("\n" + "="*60)
    print("🌡️ DS18B20 1-WIRE TEMPERATURSENSOREN TEST")
    print("="*60)
    
    try:
        # Teste ohne Konfiguration für Auto-Discovery
        print("🔍 Teste Auto-Discovery (ohne Konfiguration)...")
        reader = DS18B20Reader(config=None)  # Erzwinge Auto-Discovery
        
        if reader.get_sensor_count() == 0:
            print("❌ Keine DS18B20 Sensoren gefunden!")
            print("\n🔧 Troubleshooting:")
            print("   1. 1-Wire Interface aktiviert? (sudo raspi-config)")
            print("   2. Verkabelung prüfen (GPIO4, 3.3V, GND)")
            print("   3. Pullup-Widerstand 4.7kΩ vorhanden?")
            print("   4. Sensoren angeschlossen?")
            print("\n🔍 Direkte Überprüfung:")
            print("   ls /sys/bus/w1/devices/")
            return False
        
        print(f"✅ {reader.get_sensor_count()} DS18B20 Sensoren gefunden!")
        
        # Sensor-IDs anzeigen
        sensor_ids = reader.get_sensor_ids()
        print("\n📋 Gefundene Sensor-IDs:")
        for i, sensor_id in enumerate(sensor_ids, 1):
            print(f"   {i}. {sensor_id}")
        
        # Alle Sensoren testen
        print("\n🧪 Teste alle Sensoren...")
        temperatures = reader.read_all_temperatures()
        
        # Ergebnis anzeigen
        working_sensors = 0
        total_sensors = len(temperatures)
        
        for sensor_id, temp in temperatures.items():
            if temp is not None:
                print(f"   ✅ {sensor_id}: {temp:.1f}°C")
                working_sensors += 1
            else:
                print(f"   ❌ {sensor_id}: Lesefehler")
        
        if working_sensors == total_sensors:
            print(f"\n✅ Alle {total_sensors} DS18B20 Sensoren funktional!")
            return True
        elif working_sensors > 0:
            print(f"⚠️ {working_sensors}/{total_sensors} DS18B20 Sensoren funktional")
            print("\n❌ Defekte Sensoren:")
            for sensor_id, temp in temperatures.items():
                if temp is None:
                    print(f"   {sensor_id}")
            return False
        else:
            print("❌ Keine DS18B20 Sensoren funktional!")
            return False
            
    except Exception as e:
        print(f"❌ DS18B20 Test Fehler: {e}")
        return False


def test_dht22_sensor(config=None):
    """DHT22 Sensor testen"""
    print("\n" + "="*60)
    print("💧 DHT22 TEMPERATUR/LUFTFEUCHTIGKEIT TEST")
    print("="*60)
    
    try:
        # GPIO Pin aus Config lesen
        gpio_pin = 17
        if config and config.has_option('hardware', 'dht22_gpio'):
            gpio_pin = config.getint('hardware', 'dht22_gpio')
        
        reader = DHT22Reader(gpio_pin=gpio_pin)
        
        if not reader.dht_device:
            print("❌ DHT22 Sensor nicht verfügbar!")
            print(f"\n🔧 Troubleshooting (GPIO{gpio_pin}):")
            print("   1. DHT Library installiert? (pip install adafruit-circuitpython-dht)")
            print("   2. Verkabelung prüfen (GPIO17, 3.3V, GND)")
            print("   3. Sensor defekt?")
            return False
        
        # Sensor testen
        success = reader.test_sensor()
        
        if success:
            print("✅ DHT22 Sensor funktional!")
            return True
        else:
            print("❌ DHT22 Sensor nicht zuverlässig!")
            return False
            
    except Exception as e:
        print(f"❌ DHT22 Test Fehler: {e}")
        return False


def test_influxdb_connection(config=None):
    """InfluxDB Verbindung testen"""
    print("\n" + "="*60)
    print("🗄️ INFLUXDB VERBINDUNG TEST")
    print("="*60)
    
    try:
        from influxdb_client import InfluxDBClient
        
        # Konfiguration laden
        host = 'localhost'
        port = 8086
        token = 'pi5-token-2024'
        org = 'pi5org'
        
        if config:
            host = config.get('database', 'host', fallback=host)
            port = config.getint('database', 'port', fallback=port)
            token = config.get('database', 'token', fallback=token)
            org = config.get('database', 'org', fallback=org)
        
        url = f"http://{host}:{port}"
        print(f"📡 Teste Verbindung zu: {url}")
        
        # InfluxDB Client
        client = InfluxDBClient(url=url, token=token, org=org)
        
        # Health Check
        health = client.health()
        
        if health.status == "pass":
            print("✅ InfluxDB Verbindung erfolgreich!")
            
            # Bucket prüfen
            buckets_api = client.buckets_api()
            bucket_name = config.get('database', 'bucket', fallback='sensors') if config else 'sensors'
            
            try:
                bucket = buckets_api.find_bucket_by_name(bucket_name)
                if bucket:
                    print(f"✅ Bucket '{bucket_name}' gefunden!")
                else:
                    print(f"⚠️ Bucket '{bucket_name}' nicht gefunden")
                    
            except Exception as e:
                print(f"⚠️ Bucket Check Fehler: {e}")
            
            client.close()
            return True
        else:
            print(f"❌ InfluxDB Health Check fehlgeschlagen: {health.status}")
            return False
            
    except ImportError:
        print("❌ InfluxDB Client nicht verfügbar!")
        print("   Installation: pip install influxdb-client")
        return False
    except Exception as e:
        print(f"❌ InfluxDB Verbindungsfehler: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. InfluxDB läuft? (docker compose ps)")
        print("   2. Port 8086 erreichbar? (curl -I http://localhost:8086/health)")
        print("   3. Token korrekt?")
        return False


def test_mqtt_connection(config=None):
    """MQTT Verbindung testen"""
    print("\n" + "="*60)
    print("📡 MQTT VERBINDUNG TEST")
    print("="*60)
    
    try:
        import paho.mqtt.client as mqtt
        
        # Konfiguration laden
        broker = 'localhost'
        port = 1883
        username = ''
        password = ''
        
        if config:
            broker = config.get('mqtt', 'broker', fallback=broker)
            port = config.getint('mqtt', 'port', fallback=port)
            username = config.get('mqtt', 'username', fallback=username)
            password = config.get('mqtt', 'password', fallback=password)
        
        print(f"📡 Teste Verbindung zu: {broker}:{port}")
        
        # MQTT Client
        client = mqtt.Client()
        
        # Authentication
        if username and password:
            client.username_pw_set(username, password)
            print(f"🔐 Authentifizierung: {username}")
        
        # Verbindung testen
        connection_result = client.connect(broker, port, 60)
        
        if connection_result == 0:
            print("✅ MQTT Verbindung erfolgreich!")
            
            # Test-Nachricht senden
            topic = "pi5_heizung/test"
            message = "connection_test"
            result = client.publish(topic, message)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"✅ Test-Nachricht gesendet: {topic}")
            else:
                print(f"⚠️ Nachricht senden fehlgeschlagen: {result.rc}")
            
            client.disconnect()
            return True
        else:
            print(f"❌ MQTT Verbindung fehlgeschlagen: {connection_result}")
            return False
            
    except ImportError:
        print("❌ MQTT Client nicht verfügbar!")
        print("   Installation: pip install paho-mqtt")
        return False
    except Exception as e:
        print(f"❌ MQTT Verbindungsfehler: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. MQTT Broker läuft?")
        print("   2. Home Assistant MQTT konfiguriert?")
        print("   3. Anmeldedaten korrekt?")
        return False


def run_system_test(config_file='config.ini'):
    """Vollständiger Systemtest"""
    print("🚀 PI5 HEIZUNGS MESSER - VOLLSTÄNDIGER SYSTEMTEST")
    print("="*70)
    
    # Konfiguration laden
    config = configparser.ConfigParser()
    config_paths = [
        config_file,
        'config/config.ini',
        'config.ini.example'
    ]
    
    config_loaded = False
    for path in config_paths:
        if os.path.exists(path):
            config.read(path)
            config_loaded = True
            print(f"📋 Konfiguration geladen: {path}")
            break
    
    if not config_loaded:
        print("⚠️ Keine Konfigurationsdatei gefunden, verwende Defaults")
        config = None
    
    # Tests ausführen
    test_results = {}
    
    # Hardware Tests
    test_results['ds18b20'] = test_ds18b20_sensors(config)
    test_results['dht22'] = test_dht22_sensor(config)
    
    # Infrastruktur Tests
    test_results['influxdb'] = test_influxdb_connection(config)
    test_results['mqtt'] = test_mqtt_connection(config)
    
    # Ergebnis zusammenfassen
    print("\n" + "="*70)
    print("📊 SYSTEMTEST ERGEBNIS")
    print("="*70)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"   {test_name.upper():15} {status}")
    
    print(f"\n📈 Gesamt: {passed_tests}/{total_tests} Tests bestanden")
    
    if passed_tests == total_tests:
        print("🎉 ALLE TESTS BESTANDEN! System bereit für Produktion.")
        return True
    elif passed_tests >= 2:
        print("⚠️ TEILWEISE FUNKTIONAL. Prüfe fehlgeschlagene Komponenten.")
        return False
    else:
        print("❌ KRITISCHE FEHLER. System nicht betriebsbereit.")
        return False


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description='Pi5 Heizungs Messer - Sensor Tests')
    parser.add_argument('--config', default='config.ini', help='Konfigurationsdatei')
    parser.add_argument('--ds18b20', action='store_true', help='Nur DS18B20 Sensoren testen')
    parser.add_argument('--dht22', action='store_true', help='Nur DHT22 Sensor testen')
    parser.add_argument('--influxdb', action='store_true', help='Nur InfluxDB testen')
    parser.add_argument('--mqtt', action='store_true', help='Nur MQTT testen')
    parser.add_argument('--all', action='store_true', help='Vollständiger Systemtest (Standard)')
    
    args = parser.parse_args()
    
    try:
        # Konfiguration laden
        config = None
        if os.path.exists(args.config):
            config = configparser.ConfigParser()
            config.read(args.config)
        
        # Spezifische Tests
        if args.ds18b20:
            success = test_ds18b20_sensors(config)
        elif args.dht22:
            success = test_dht22_sensor(config)
        elif args.influxdb:
            success = test_influxdb_connection(config)
        elif args.mqtt:
            success = test_mqtt_connection(config)
        else:
            # Vollständiger Test (Standard)
            success = run_system_test(args.config)
        
        # Exit Code setzen
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n👋 Tests abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
