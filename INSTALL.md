
# 🛠️ INSTALLATION – Sprachsteuerung für FHEM

Diese Anleitung beschreibt die vollständige Einrichtung des lokalen Sprachsystems auf einem Linux-System (z. B. Debian VM unter Proxmox).

---

## 🔧 Voraussetzungen

- Debian/Linux mit Python 3.11
- Soundgerät (z. B. PowerConf S3, als ALSA-Device eingebunden)
- NVIDIA-GPU für CUDA (empfohlen)
- FHEM-Server (z. B. unter <FHEM-IP>:8083)

---

## 📦 Python-Umgebung einrichten

```bash
sudo apt install python3.11 python3.11-venv python3-pip libportaudio2 ffmpeg
python3.11 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt
```

**Beispiel für `requirements.txt`:**

```
vosk
sounddevice
samplerate
numpy
librosa
faster-whisper
TTS
llama-cpp-python
requests
```

---

## 🎙️ Audio einrichten

### 📁 Konfigurationsdateien anlegen:

```bash
echo "plughw:0,0" > /opt/script/audio_device.conf
echo "4" > /opt/script/audio_input.conf
echo "1.0" > /opt/script/mic_gain.conf
```

Passe die Werte je nach deinem Setup an.

---

## 📁 Verzeichnisstruktur vorbereiten

```bash
mkdir -p /opt/script
mkdir -p /opt/sound/{responses,confirm,error,timer}
mkdir -p /opt/vosk
```

---

## 📥 Modelle herunterladen

### 🧠 Vosk (Wakeword + Transkription)
- Modell: `vosk-model-small-de-0.15`
- https://alphacephei.com/vosk/models

### 🗣️ Coqui TTS:
```bash
# Automatisch beim ersten Aufruf heruntergeladen:
python3 -m TTS.api
```

### 🤖 GPT (z. B. TinyLlama oder Mistral):
```bash
# Modell platzieren unter:
cp mistral-7b-instruct-v0.1.Q4_K_M.gguf /opt/
```

---

## 🧠 Sprachlogik starten

### 🖥️ Als Service einrichten:

```ini
# /etc/systemd/system/voice_system.service
[Unit]
Description=Starte gesamtes Sprachsystem (Find Audio + Wakeword)
After=network.target sound.target

[Service]
Type=simple
ExecStart=/opt/script/start_voice_system.sh
WorkingDirectory=/opt/script
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
```

Aktivieren:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable voice_system
sudo systemctl start voice_system
```

---

## ✅ Test

```bash
journalctl -u voice_system.service -f
```

Dann z. B. sagen: **„Alexa, wie ist die Temperatur im Wohnzimmer?“**

---

## 🔒 Sicherheit

- Passwörter in `/opt/script/fhem_auth.conf` speichern:

```ini
[FHEM]
url = http://<FHEM-IP>:8083/fhem
user = <BENUTZER>
pass = dein_passwort
```

---

## 📄 Dateien

- `wakeword_niko.py`: Hauptsystem
- `gpt_temp.py`: Temperatur
- `timer.py`: Timer
- `gpt_to_fhem.py`: FHEM-Befehle
- `filter.py`: Textvereinfachung

---

## 📢 Letzter Hinweis

Dieses System läuft **vollständig lokal** – ideal für Datenschutz, Geschwindigkeit und Kontrolle!

