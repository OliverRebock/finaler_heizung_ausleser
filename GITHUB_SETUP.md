# GitHub Repository Setup für Pi5 Heizungs Messer
# =================================================

## 🚀 Repository zu GitHub hochladen

### Option 1: Über GitHub Web Interface (Empfohlen)

1. **Gehe zu GitHub.com** und melde dich an
2. **Klicke auf "New repository"** (grüner Button)
3. **Repository Settings:**
   - Repository name: `pi5-heizungs-messer` oder `Heizung_auslesen`
   - Description: `Python-based heating monitoring system for Raspberry Pi 5 with MQTT/InfluxDB integration`
   - Visibility: `Public` oder `Private` (deine Wahl)
   - ❌ **NICHT** "Initialize this repository with README" ankreuzen (wir haben bereits Dateien)

4. **Repository erstellen** → "Create repository"

5. **Local Repository verknüpfen** (diese Befehle im Terminal ausführen):

```bash
# Remote Repository hinzufügen (ersetze USERNAME mit deinem GitHub Username)
git remote add origin https://github.com/USERNAME/pi5-heizungs-messer.git

# oder SSH falls konfiguriert:
# git remote add origin git@github.com:USERNAME/pi5-heizungs-messer.git

# Zum GitHub Repository pushen
git push -u origin main
```

### Option 2: GitHub CLI (falls installiert)

```bash
# Repository auf GitHub erstellen und pushen
gh repo create pi5-heizungs-messer --public --description "Pi5 heating monitoring system" --push
```

## 📋 Repository Informationen

**Projekt:** Pi5 Heizungs Messer - Heizung_auslesen
**Typ:** Python IoT Projekt für Raspberry Pi 5
**Lizenz:** MIT oder persönlicher Gebrauch

### Repository Beschreibung für GitHub:

```
Python-based heating monitoring system for Raspberry Pi 5

🌡️ Features:
• DS18B20 1-Wire temperature sensors (up to 8 heating circuits)
• DHT22 ambient temperature & humidity monitoring  
• InfluxDB time-series data storage
• MQTT integration with Home Assistant auto-discovery
• Docker-based deployment
• Comprehensive testing and documentation

🚀 Ready for production use on Raspberry Pi 5
```

### Tags/Topics für Repository:

```
raspberry-pi
raspberry-pi-5
python
iot
heating-monitoring
mqtt
influxdb
home-assistant
ds18b20
dht22
temperature-sensor
smart-home
docker
```

## 🔧 Nach dem Upload

### 1. Repository Settings konfigurieren:
- **About**: Beschreibung und Website hinzufügen
- **Topics**: Tags hinzufügen für bessere Auffindbarkeit
- **Releases**: Erste Version taggen

### 2. GitHub Actions (Optional):
- CI/CD für automatische Tests
- Deployment Scripts für Pi5

### 3. Issues Templates:
- Bug Report Template
- Feature Request Template

### 4. Weitere Dokumentation:
- Wiki für detaillierte Anleitungen
- GitHub Pages für Projekt-Website

## 📝 Beispiel Commands

```bash
# Status prüfen
git status

# Remote prüfen  
git remote -v

# Neue Änderungen pushen
git add .
git commit -m "Update: Beschreibung der Änderungen"
git push origin main

# Branch erstellen für Features
git checkout -b feature/neue-funktion
git push -u origin feature/neue-funktion
```

## 🆘 Troubleshooting

### Authentication Probleme:
```bash
# GitHub Token setup (falls HTTPS verwendet)
git config --global credential.helper store

# SSH Key setup (empfohlen)
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub  # Inhalt zu GitHub SSH Keys hinzufügen
```

### Repository URL ändern:
```bash
git remote set-url origin https://github.com/USERNAME/NEUER-NAME.git
```
