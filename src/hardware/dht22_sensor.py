#!/usr/bin/env python3
"""
DHT22 Temperatur/Luftfeuchtigkeitssensor Reader für Pi5
======================================================

Klasse für das Auslesen von DHT22 Sensoren am Raspberry Pi 5.
Verwendet Adafruit CircuitPython Library für zuverlässige Messwerte.

Autor: Pi5 Heizungs Messer Project
"""

import time
import logging
from typing import Dict, Optional
import board
import digitalio

try:
    import adafruit_dht
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False
    print("❌ DHT Library nicht verfügbar - installiere: pip install adafruit-circuitpython-dht")

logger = logging.getLogger(__name__)


class DHT22Reader:
    """
    DHT22 Sensor Reader für Raspberry Pi 5
    Temperatur und Luftfeuchtigkeit
    """
    
    def __init__(self, gpio_pin: int = 18):
        """
        Initialisiere DHT22 Reader
        
        Args:
            gpio_pin: GPIO Pin Nummer (Board Pinout)
        """
        self.gpio_pin = gpio_pin
        self.dht_device = None
        self.last_reading = None
        self.last_reading_time = 0
        self.min_read_interval = 2.0  # DHT22 benötigt mindestens 2s zwischen Messungen
        
        if not DHT_AVAILABLE:
            logger.error("❌ DHT Library nicht verfügbar!")
            return
        
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """DHT22 Sensor initialisieren"""
        try:
            # GPIO Pin zu Board Pin konvertieren
            pin_map = {
                17: board.D17,
                18: board.D18,
                22: board.D22,
                23: board.D23,
                24: board.D24,
                25: board.D25,
                27: board.D27
            }
            
            if self.gpio_pin not in pin_map:
                logger.error(f"❌ GPIO Pin {self.gpio_pin} nicht unterstützt")
                logger.error(f"   Unterstützte Pins: {list(pin_map.keys())}")
                return
            
            board_pin = pin_map[self.gpio_pin]
            
            # DHT22 Sensor initialisieren
            self.dht_device = adafruit_dht.DHT22(board_pin, use_pulseio=False)
            
            logger.info(f"✅ DHT22 Sensor initialisiert auf GPIO{self.gpio_pin}")
            
            # Initial Test
            test_data = self._read_sensor_raw()
            if test_data:
                logger.info(f"   Test-Messung: {test_data['temperature']:.1f}°C, {test_data['humidity']:.1f}%")
            else:
                logger.warning("⚠️ DHT22 Initial-Test fehlgeschlagen")
                
        except Exception as e:
            logger.error(f"❌ DHT22 Initialisierung fehlgeschlagen: {e}")
            self.dht_device = None
    
    def _read_sensor_raw(self) -> Optional[Dict[str, float]]:
        """Raw Sensor-Daten lesen (ohne Caching)"""
        if not self.dht_device:
            return None
        
        try:
            # DHT22 auslesen
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity
            
            # Plausibilitätsprüfung
            if temperature is None or humidity is None:
                return None
            
            # Temperatur Bereich: -40°C bis +80°C
            if temperature < -40 or temperature > 80:
                logger.warning(f"⚠️ Temperatur außerhalb Bereich: {temperature}°C")
                return None
            
            # Luftfeuchtigkeit Bereich: 0-100%
            if humidity < 0 or humidity > 100:
                logger.warning(f"⚠️ Luftfeuchtigkeit außerhalb Bereich: {humidity}%")
                return None
            
            return {
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'timestamp': time.time()
            }
            
        except RuntimeError as e:
            # DHT Sensoren können gelegentlich Lesefehler haben
            logger.debug(f"DHT22 Lesefehler (normal): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ DHT22 Unerwarteter Fehler: {e}")
            return None
    
    def read_sensor(self, use_cache: bool = True) -> Optional[Dict[str, float]]:
        """
        DHT22 Sensor auslesen
        
        Args:
            use_cache: Cached Werte verwenden falls innerhalb min_read_interval
            
        Returns:
            Dict mit temperature, humidity, timestamp oder None bei Fehler
        """
        current_time = time.time()
        
        # Cache prüfen
        if (use_cache and 
            self.last_reading and 
            (current_time - self.last_reading_time) < self.min_read_interval):
            logger.debug(f"DHT22 Cache verwendet (vor {current_time - self.last_reading_time:.1f}s)")
            return self.last_reading
        
        # Neue Messung
        data = self._read_sensor_raw()
        
        if data:
            self.last_reading = data
            self.last_reading_time = current_time
            logger.debug(f"DHT22 gelesen: {data['temperature']}°C, {data['humidity']}%")
        
        return data
    
    def read_sensor_with_retry(self, max_retries: int = 3, retry_delay: float = 0.5) -> Optional[Dict[str, float]]:
        """
        DHT22 mit Wiederholungsversuchen lesen
        
        Args:
            max_retries: Maximale Anzahl Versuche
            retry_delay: Pause zwischen Versuchen in Sekunden
        """
        for attempt in range(max_retries):
            data = self.read_sensor(use_cache=False)
            
            if data:
                return data
            
            if attempt < max_retries - 1:
                logger.debug(f"DHT22 Versuch {attempt + 1} fehlgeschlagen, wiederhole...")
                time.sleep(retry_delay)
        
        logger.warning(f"⚠️ DHT22: Alle {max_retries} Versuche fehlgeschlagen")
        return None
    
    def get_temperature(self) -> Optional[float]:
        """Nur Temperatur lesen"""
        data = self.read_sensor()
        return data['temperature'] if data else None
    
    def get_humidity(self) -> Optional[float]:
        """Nur Luftfeuchtigkeit lesen"""
        data = self.read_sensor()
        return data['humidity'] if data else None
    
    def test_sensor(self) -> bool:
        """Sensor-Funktionalität testen"""
        logger.info("🧪 Teste DHT22 Sensor...")
        
        if not self.dht_device:
            logger.error("❌ DHT22 Sensor nicht initialisiert")
            return False
        
        # Mehrere Testmessungen
        successful_reads = 0
        total_attempts = 5
        
        for i in range(total_attempts):
            data = self.read_sensor(use_cache=False)
            
            if data:
                successful_reads += 1
                logger.info(f"   Messung {i+1}: {data['temperature']:.1f}°C, {data['humidity']:.1f}%")
            else:
                logger.warning(f"   Messung {i+1}: Fehlgeschlagen")
            
            time.sleep(2.5)  # DHT22 benötigt Pause zwischen Messungen
        
        success_rate = (successful_reads / total_attempts) * 100
        logger.info(f"📊 DHT22 Test: {successful_reads}/{total_attempts} erfolgreich ({success_rate:.0f}%)")
        
        # Mindestens 60% Erfolgsrate als OK bewerten
        return success_rate >= 60
    
    def get_sensor_info(self) -> Dict:
        """Sensor-Informationen zurückgeben"""
        return {
            'type': 'DHT22',
            'gpio_pin': self.gpio_pin,
            'available': self.dht_device is not None,
            'last_reading': self.last_reading,
            'last_reading_time': self.last_reading_time
        }
    
    def cleanup(self):
        """Sensor-Ressourcen freigeben"""
        if self.dht_device:
            try:
                self.dht_device.exit()
                logger.info("🧹 DHT22 Cleanup abgeschlossen")
            except:
                pass
        self.dht_device = None


def main():
    """Test-Funktion für DHT22 Reader"""
    import argparse
    
    # Logging für Tests
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = argparse.ArgumentParser(description='DHT22 Sensor Test')
    parser.add_argument('--pin', type=int, default=17, help='GPIO Pin Nummer (default: 17)')
    parser.add_argument('--test', action='store_true', help='Umfangreichen Sensor-Test ausführen')
    parser.add_argument('--continuous', action='store_true', help='Kontinuierliche Messungen')
    parser.add_argument('--interval', type=int, default=5, help='Intervall für kontinuierliche Messungen')
    
    args = parser.parse_args()
    
    if not DHT_AVAILABLE:
        print("❌ DHT Library nicht verfügbar!")
        print("   Installation: pip install adafruit-circuitpython-dht")
        return
    
    # DHT22 Reader initialisieren
    reader = DHT22Reader(gpio_pin=args.pin)
    
    try:
        if args.test:
            # Umfangreicher Test
            success = reader.test_sensor()
            print(f"\n📊 DHT22 Test: {'✅ Bestanden' if success else '❌ Fehlgeschlagen'}")
            
        elif args.continuous:
            # Kontinuierliche Messungen
            print(f"\n🔄 Kontinuierliche DHT22 Messungen (alle {args.interval}s)")
            print("   Drücke Ctrl+C zum Beenden\n")
            
            try:
                while True:
                    data = reader.read_sensor_with_retry()
                    
                    if data:
                        print(f"{time.strftime('%H:%M:%S')} - "
                              f"Temp: {data['temperature']:5.1f}°C, "
                              f"Hum: {data['humidity']:5.1f}%")
                    else:
                        print(f"{time.strftime('%H:%M:%S')} - Lesefehler")
                    
                    time.sleep(args.interval)
                    
            except KeyboardInterrupt:
                print("\n👋 Messungen beendet")
                
        else:
            # Einzelmessung
            print(f"\n🌡️ DHT22 Sensor Test (GPIO{args.pin}):")
            
            data = reader.read_sensor_with_retry()
            
            if data:
                print(f"   Temperatur: {data['temperature']:.1f}°C")
                print(f"   Luftfeuchtigkeit: {data['humidity']:.1f}%")
                print(f"   Messzeitpunkt: {time.strftime('%H:%M:%S', time.localtime(data['timestamp']))}")
            else:
                print("   ❌ Sensor konnte nicht gelesen werden")
                
    finally:
        reader.cleanup()


if __name__ == "__main__":
    main()
