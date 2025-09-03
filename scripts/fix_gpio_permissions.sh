#!/bin/bash
# GPIO Permissions Fix für Pi5
# =============================

echo "🔧 GPIO Permissions Fix für Pi5"
echo "================================"

# Prüfe aktuelle Benutzer-Gruppen
echo "👤 Aktuelle Benutzer-Gruppen:"
groups $USER

echo ""
echo "🔍 Prüfe GPIO Gruppen..."

# GPIO Gruppe hinzufügen
if groups $USER | grep -q gpio; then
    echo "✅ Benutzer ist bereits in GPIO-Gruppe"
else
    echo "➕ Füge Benutzer zur GPIO-Gruppe hinzu..."
    sudo usermod -aG gpio $USER
    echo "✅ Benutzer zur GPIO-Gruppe hinzugefügt"
fi

# I2C Gruppe (falls benötigt)
if groups $USER | grep -q i2c; then
    echo "✅ Benutzer ist bereits in I2C-Gruppe"
else
    echo "➕ Füge Benutzer zur I2C-Gruppe hinzu..."
    sudo usermod -aG i2c $USER
    echo "✅ Benutzer zur I2C-Gruppe hinzugefügt"
fi

# SPI Gruppe (falls benötigt)
if groups $USER | grep -q spi; then
    echo "✅ Benutzer ist bereits in SPI-Gruppe"
else
    echo "➕ Füge Benutzer zur SPI-Gruppe hinzu..."
    sudo usermod -aG spi $USER
    echo "✅ Benutzer zur SPI-Gruppe hinzugefügt"
fi

echo ""
echo "🔍 GPIO Device Permissions:"
ls -la /dev/gpio* 2>/dev/null || echo "⚠️ Keine /dev/gpio* Devices gefunden"
ls -la /dev/gpiomem 2>/dev/null || echo "⚠️ /dev/gpiomem nicht gefunden"

echo ""
echo "🔍 GPIO Export Permissions:"
ls -la /sys/class/gpio/export 2>/dev/null || echo "⚠️ GPIO Export nicht verfügbar"

echo ""
echo "📋 GPIO Interface Status:"
if [ -d "/sys/class/gpio" ]; then
    echo "✅ GPIO Sysfs Interface verfügbar"
else
    echo "❌ GPIO Sysfs Interface nicht verfügbar"
fi

echo ""
echo "🔧 Setze GPIO Permissions..."

# GPIO Memory Device Permissions
if [ -e "/dev/gpiomem" ]; then
    sudo chmod 664 /dev/gpiomem
    sudo chgrp gpio /dev/gpiomem
    echo "✅ /dev/gpiomem Permissions gesetzt"
else
    echo "⚠️ /dev/gpiomem nicht gefunden"
fi

# GPIO Chip Permissions
for chip in /dev/gpiochip*; do
    if [ -e "$chip" ]; then
        sudo chmod 664 "$chip"
        sudo chgrp gpio "$chip"
        echo "✅ $chip Permissions gesetzt"
    fi
done

echo ""
echo "📊 Aktuelle Permissions:"
echo "👤 Benutzer-Gruppen nach Änderung:"
groups $USER

echo ""
echo "🔄 WICHTIG: Änderungen werden nach NEUANMELDUNG aktiv!"
echo ""
echo "💡 Optionen:"
echo "   1. Ausloggen und wieder einloggen"
echo "   2. Neues Terminal öffnen"
echo "   3. System neu starten (empfohlen)"
echo "   4. Temporär: sudo python scripts/test_sensors_direct.py"
echo ""
echo "🧪 Nach Neuanmeldung testen:"
echo "   python scripts/test_sensors_direct.py"
