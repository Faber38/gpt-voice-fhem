# 🛠️ GPT-Voice-FHEM – Installationsanleitung

## ✅ Voraussetzungen

- Debian-basiertes Linux-System
- Python 3.11
- Git
- Soundkarte mit Mikrofon (z. B. PowerConf S3)
- FHEM mit HTTP-Auth (Username & Passwort bekannt)

---

## 📁 Verzeichnisstruktur

Das Projekt liegt unter `/opt/`:

/opt/ ├── script/ # Alle Python-Skripte und Konfigs ├── sound/ # Audio-Antworten (responses, confirm, error) ├── vosk/ # Vosk-Modelle ├── phi-2.Q4_K_M.gguf # Optional: GPT-Modell ├── tinyllama... # GPT-Modell für Sprachverarbeitung └── venv/ # Python-Virtualenv


---

## 🔧 Installation

### 1. Python Virtualenv

```bash
sudo apt install python3.11-venv
cd /opt
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Benötigte Pakete:

pip install sounddevice samplerate vosk requests numpy

2. Vosk Modell installieren

mkdir -p /opt/vosk
cd /opt/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
unzip vosk-model-small-de-0.15.zip
mv vosk-model-small-de-0.15 vosk-de

3. Konfiguration
🔊 Audio

    /opt/script/audio_index.conf → enthält z. B. 4 (Index für sounddevice)

    /opt/script/audio_device.conf → enthält z. B. hw:CARD=S3,DEV=0

💡 Geräte

    /opt/script/device.txt

Küche Licht an|ein|einschalten
Küche Licht aus|ausschalten
Wohnzimmer Licht an|ein|einschalten
...

▶️ Starten
Manuell testen

/opt/venv/bin/python /opt/script/wakeword_niko.py

Systemd-Service

# /etc/systemd/system/voice-fhem.service

[Unit]
Description=Voice-FHEM Wakeword System
After=network.target

[Service]
ExecStart=/opt/venv/bin/python /opt/script/wakeword_niko.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target

systemctl daemon-reexec
systemctl enable --now voice-fhem.service

🧪 Debug / Tests

/opt/venv/bin/python /opt/script/mic_test.py
/opt/venv/bin/python /opt/script/read_command.py
/opt/venv/bin/python /opt/script/gpt_to_fhem.py "küche licht an"

ℹ️ Hinweise

    Die Antwort-WAVs liegen unter /opt/sound/

    Alle Audio-Dateien sind 48 kHz, stereo

    FHEM-Befehle werden als set GptVoiceCommand gesendet

    Die Bestätigung (z. B. „okay erledigt“) erfolgt aus /opt/sound/confirm

Viel Spaß mit deiner lokalen Sprachsteuerung!
