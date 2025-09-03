# 🚀 Pi5 Installation Guide - Komplette Anleitung
# ================================================

## ⚠️ WICHTIG: Diese Befehle auf dem Pi5 ausführen, nicht auf Windows!

## 📋 Schritt-für-Schritt Installation

### 1️⃣ **Projekt auf Pi5 übertragen**

#### Option A: Git Clone (Empfohlen)
```bash
# SSH Verbindung zum Pi5
ssh pi@<deine-pi5-ip-adresse>

# Projekt klonen
git clone https://github.com/OliverRebock/finaler_heizung_ausleser.git
cd finaler_heizung_ausleser

# Verzeichnis prüfen
ls -la scripts/
```

#### Option B: SCP Transfer (von Windows)
```powershell
# Von Windows PowerShell aus:
scp -r "c:\Users\reboc\OneDrive\Desktop\Heizung_auslesen\*" pi@<pi5-ip>:/home/pi/heizung_projekt/
```

### 2️⃣ **Scripts ausführbar machen (AUF DEM PI5!)**
```bash
# Auf dem Pi5 Terminal:
cd finaler_heizung_ausleser

# Scripts ausführbar machen
chmod +x scripts/install_dependencies.sh
chmod +x scripts/deploy_docker.sh
chmod +x scripts/test_sensors.py

# Prüfen ob Scripts da sind
ls -la scripts/
```

### 3️⃣ **Dependencies installieren**
```bash
# Auf dem Pi5:
bash scripts/install_dependencies.sh
```

**Was passiert:**
- ✅ System Updates
- ✅ Python 3 + GPIO Libraries  
- ✅ Docker Installation
- ✅ Docker Compose Check
- ✅ 1-Wire Support
- ✅ MQTT Tools
- ✅ Virtual Environment
- ✅ Python Packages

### 4️⃣ **Docker Services starten**
```bash
# Auf dem Pi5:
bash scripts/deploy_docker.sh
```

### 5️⃣ **Hardware testen**
```bash
# Auf dem Pi5:
source venv/bin/activate
python scripts/test_sensors.py
```

## 🖥️ **SSH Verbindung zum Pi5**

### Windows zu Pi5 verbinden:
```powershell
# Pi5 IP-Adresse herausfinden (auf dem Pi5):
hostname -I

# Von Windows aus verbinden:
ssh pi@192.168.1.XXX
# Oder mit PuTTY
```

### Erste SSH Verbindung:
```bash
# Standard Raspberry Pi Login:
Username: pi
Password: raspberry (oder dein geändertes Passwort)
```

## 🔧 **Alternativer Upload per WinSCP/FileZilla**

1. **WinSCP** oder **FileZilla** öffnen
2. **Verbindung** zu Pi5: `sftp://pi@<pi5-ip>`
3. **Lokaler Ordner**: `c:\Users\reboc\OneDrive\Desktop\Heizung_auslesen`
4. **Remote Ordner**: `/home/pi/heizung_projekt`
5. **Upload** des kompletten Ordners
6. **SSH Terminal** öffnen und `chmod` ausführen

## 📁 **Verzeichnisstruktur auf Pi5 prüfen**

```bash
# Nach Upload prüfen:
cd /home/pi/finaler_heizung_ausleser
tree . || ls -la

# Sollte zeigen:
# scripts/
#   install_dependencies.sh
#   deploy_docker.sh
#   test_sensors.py
# src/
# config/
# etc.
```

## ⚡ **Quick Commands für Pi5**

```bash
# System Info
uname -a                    # Kernel Info
cat /etc/os-release        # OS Version
free -h                    # Memory
df -h                      # Disk Space
vcgencmd measure_temp      # CPU Temperature

# Docker Status
systemctl status docker    # Docker Service Status
docker --version          # Docker Version
docker-compose --version  # Compose Version

# GPIO Status
gpio readall              # GPIO Pin Status (falls installiert)
ls /sys/bus/w1/devices/   # 1-Wire Devices
```

## 🚨 **Häufige Probleme**

### Problem: "Permission denied"
```bash
# Lösung:
sudo chmod +x scripts/*.sh
```

### Problem: "Command not found"
```bash
# Lösung: Shebang prüfen
head -1 scripts/install_dependencies.sh
# Sollte sein: #!/bin/bash
```

### Problem: "No such file or directory"
```bash
# Lösung: Verzeichnis prüfen
pwd
ls -la scripts/
```

### Problem: Docker Permission denied
```bash
# Lösung: User zur Docker-Gruppe hinzufügen
sudo usermod -aG docker $USER
# Dann neu anmelden (logout/login)
```

## 📱 **Nach erfolgreicher Installation**

Services erreichbar unter:
- **InfluxDB**: `http://<pi5-ip>:8086`
- **Grafana**: `http://<pi5-ip>:3000`

## 🎯 **Nächste Schritte**

1. SSH zum Pi5 verbinden
2. Projekt klonen/uploaden  
3. Scripts ausführbar machen
4. Installation starten
5. Hardware testen
6. Services konfigurieren

**Alles läuft dann auf dem Pi5, nicht auf Windows!** 🚀
