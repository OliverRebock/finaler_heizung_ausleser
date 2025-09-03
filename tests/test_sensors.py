#!/usr/bin/env python3
"""
Unit Tests für Pi5 Heizungs Messer - Sensoren
==============================================

pytest Tests für die Hardware-Sensor Klassen

Autor: Pi5 Heizungs Messer Project
"""

import pytest
import unittest.mock as mock
import sys
from pathlib import Path

# Projekt Root zum Path hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from hardware.ds18b20_sensor import DS18B20Reader
from hardware.dht22_sensor import DHT22Reader


class TestDS18B20Reader:
    """Tests für DS18B20Reader Klasse"""
    
    def test_initialization(self):
        """Test DS18B20Reader Initialisierung"""
        with mock.patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            reader = DS18B20Reader()
            assert reader.w1_device_path == "/sys/bus/w1/devices/"
            assert reader.sensor_ids == []
    
    @mock.patch('os.path.exists')
    @mock.patch('os.listdir')
    def test_sensor_discovery(self, mock_listdir, mock_exists):
        """Test automatische Sensor-Erkennung"""
        mock_exists.return_value = True
        mock_listdir.return_value = ['28-0000000001', '28-0000000002', 'w1_bus_master1']
        
        reader = DS18B20Reader()
        assert len(reader.sensor_ids) == 2
        assert '28-0000000001' in reader.sensor_ids
        assert '28-0000000002' in reader.sensor_ids
    
    def test_temperature_parsing(self):
        """Test Temperatur-Parsing aus Sensor-Datei"""
        mock_content = """a1 01 4b 46 7f ff 0c 10 7c : crc=7c YES
a1 01 4b 46 7f ff 0c 10 7c t=26062"""
        
        with mock.patch('builtins.open', mock.mock_open(read_data=mock_content)):
            with mock.patch('os.path.exists', return_value=True):
                reader = DS18B20Reader()
                temp = reader.read_temperature('28-0000000001')
                assert temp == 26.06
    
    def test_invalid_temperature_data(self):
        """Test fehlerhafte Sensor-Daten"""
        mock_content = """a1 01 4b 46 7f ff 0c 10 7c : crc=7c NO
a1 01 4b 46 7f ff 0c 10 7c t=26062"""
        
        with mock.patch('builtins.open', mock.mock_open(read_data=mock_content)):
            with mock.patch('os.path.exists', return_value=True):
                reader = DS18B20Reader()
                temp = reader.read_temperature('28-0000000001')
                assert temp is None
    
    def test_plausibility_check(self):
        """Test Plausibilitätsprüfung für Temperaturen"""
        # Temperatur zu niedrig
        mock_content_low = """a1 01 4b 46 7f ff 0c 10 7c : crc=7c YES
a1 01 4b 46 7f ff 0c 10 7c t=-60000"""
        
        with mock.patch('builtins.open', mock.mock_open(read_data=mock_content_low)):
            with mock.patch('os.path.exists', return_value=True):
                reader = DS18B20Reader()
                temp = reader.read_temperature('28-0000000001')
                assert temp is None
        
        # Temperatur zu hoch
        mock_content_high = """a1 01 4b 46 7f ff 0c 10 7c : crc=7c YES
a1 01 4b 46 7f ff 0c 10 7c t=130000"""
        
        with mock.patch('builtins.open', mock.mock_open(read_data=mock_content_high)):
            with mock.patch('os.path.exists', return_value=True):
                reader = DS18B20Reader()
                temp = reader.read_temperature('28-0000000001')
                assert temp is None


class TestDHT22Reader:
    """Tests für DHT22Reader Klasse"""
    
    @mock.patch('hardware.dht22_sensor.DHT_AVAILABLE', True)
    @mock.patch('hardware.dht22_sensor.adafruit_dht')
    @mock.patch('hardware.dht22_sensor.board')
    def test_initialization(self, mock_board, mock_dht):
        """Test DHT22Reader Initialisierung"""
        mock_board.D17 = "GPIO17"
        mock_dht.DHT22.return_value = mock.Mock()
        
        reader = DHT22Reader(gpio_pin=17)
        assert reader.gpio_pin == 17
        assert reader.min_read_interval == 2.0
    
    @mock.patch('hardware.dht22_sensor.DHT_AVAILABLE', True)
    @mock.patch('hardware.dht22_sensor.adafruit_dht')
    @mock.patch('hardware.dht22_sensor.board')
    def test_valid_reading(self, mock_board, mock_dht):
        """Test gültige DHT22 Messung"""
        mock_board.D17 = "GPIO17"
        mock_sensor = mock.Mock()
        mock_sensor.temperature = 23.5
        mock_sensor.humidity = 65.2
        mock_dht.DHT22.return_value = mock_sensor
        
        reader = DHT22Reader(gpio_pin=17)
        data = reader._read_sensor_raw()
        
        assert data is not None
        assert data['temperature'] == 23.5
        assert data['humidity'] == 65.2
        assert 'timestamp' in data
    
    @mock.patch('hardware.dht22_sensor.DHT_AVAILABLE', True)
    @mock.patch('hardware.dht22_sensor.adafruit_dht')
    @mock.patch('hardware.dht22_sensor.board')
    def test_invalid_readings(self, mock_board, mock_dht):
        """Test ungültige DHT22 Messwerte"""
        mock_board.D17 = "GPIO17"
        mock_sensor = mock.Mock()
        
        # Test None-Werte
        mock_sensor.temperature = None
        mock_sensor.humidity = 65.2
        mock_dht.DHT22.return_value = mock_sensor
        
        reader = DHT22Reader(gpio_pin=17)
        data = reader._read_sensor_raw()
        assert data is None
        
        # Test Werte außerhalb Bereich
        mock_sensor.temperature = -50.0  # Zu niedrig
        mock_sensor.humidity = 65.2
        data = reader._read_sensor_raw()
        assert data is None
        
        mock_sensor.temperature = 23.5
        mock_sensor.humidity = 110.0  # Zu hoch
        data = reader._read_sensor_raw()
        assert data is None
    
    @mock.patch('hardware.dht22_sensor.DHT_AVAILABLE', True)
    @mock.patch('hardware.dht22_sensor.adafruit_dht')
    @mock.patch('hardware.dht22_sensor.board')
    def test_runtime_error_handling(self, mock_board, mock_dht):
        """Test RuntimeError Behandlung (normale DHT22 Lesefehler)"""
        mock_board.D17 = "GPIO17"
        mock_sensor = mock.Mock()
        mock_sensor.temperature = mock.PropertyMock(side_effect=RuntimeError("DHT sensor not ready"))
        mock_dht.DHT22.return_value = mock_sensor
        
        reader = DHT22Reader(gpio_pin=17)
        data = reader._read_sensor_raw()
        assert data is None
    
    @mock.patch('hardware.dht22_sensor.DHT_AVAILABLE', False)
    def test_library_not_available(self):
        """Test Verhalten wenn DHT Library nicht verfügbar"""
        reader = DHT22Reader(gpio_pin=17)
        assert reader.dht_device is None


if __name__ == '__main__':
    pytest.main([__file__])
