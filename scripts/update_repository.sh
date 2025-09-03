#!/bin/bash
# Auto-Update Script für Pi5 Heizungs-Messer
# ===========================================

set -e

echo "🔄 Pi5 Heizungs-Messer - Repository Update"
echo "=========================================="

# Verzeichnis prüfen
if [ ! -d "/home/pi/finaler_heizung_ausleser" ]; then
    echo "❌ Repository nicht gefunden!"
    echo "💡 Erstinstallation:"
    echo "curl -fsSL https://raw.githubusercontent.com/OliverRebock/finaler_heizung_ausleser/main/scripts/github_deploy.sh | bash"
    exit 1
fi

cd /home/pi/finaler_heizung_ausleser

# Backup der aktuellen config.ini
if [ -f "config.ini" ]; then
    cp config.ini config.ini.backup
    echo "✅ config.ini gesichert"
fi

# Git Status prüfen
echo "🔍 Prüfe Repository Status..."
git fetch origin

# Zeige verfügbare Updates
BEHIND=$(git rev-list --count HEAD..origin/main)
if [ "$BEHIND" -eq 0 ]; then
    echo "✅ Repository ist bereits aktuell"
    exit 0
else
    echo "📥 $BEHIND Update(s) verfügbar"
fi

# Lokale Änderungen prüfen
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ Lokale Änderungen erkannt"
    echo "💾 Sichere lokale Änderungen..."
    git stash push -m "Auto-stash vor Update $(date)"
    STASHED=true
else
    STASHED=false
fi

# Update durchführen
echo "📥 Lade Updates..."
git pull origin main

# Dependencies aktualisieren
if [ -f "requirements.txt" ]; then
    echo "📦 Aktualisiere Python Dependencies..."
    source venv/bin/activate 2>/dev/null || echo "⚠️ Virtual Environment nicht gefunden"
    pip install -r requirements.txt --upgrade
fi

# Scripts ausführbar machen
echo "🔧 Setze Script-Permissions..."
chmod +x scripts/*.sh 2>/dev/null || true

# Konfiguration wiederherstellen
if [ -f "config.ini.backup" ]; then
    if [ ! -f "config.ini" ] || ! cmp -s "config.ini" "config.ini.backup"; then
        cp config.ini.backup config.ini
        echo "✅ Konfiguration wiederhergestellt"
    fi
fi

# Lokale Änderungen wiederherstellen
if [ "$STASHED" = true ]; then
    echo "🔄 Stelle lokale Änderungen wieder her..."
    git stash pop || echo "⚠️ Merge-Konflikte möglich - manuell prüfen"
fi

# Changelog anzeigen
echo ""
echo "📋 Neueste Änderungen:"
git log --oneline -5

echo ""
echo "✅ Update abgeschlossen!"
echo ""
echo "🧪 Empfohlene Tests:"
echo "   python scripts/test_sensors_direct.py"
echo "   bash scripts/deploy_docker.sh"
echo ""
echo "📁 Backup der alten Konfiguration: config.ini.backup"
