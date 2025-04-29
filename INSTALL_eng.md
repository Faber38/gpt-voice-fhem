
# 🛠️ INSTALLATION – Voice Control System for FHEM

This guide describes the complete setup for the local voice control system on a Linux machine (e.g., Debian VM on Proxmox).

---

## 🔧 Requirements

- Debian/Linux with Python 3.11
- Audio device (e.g., PowerConf S3 connected via ALSA)
- NVIDIA GPU with CUDA support (recommended)
- FHEM server (e.g., at <FHEM-IP>:8083)

---

## 📦 Setup Python Environment

```bash
sudo apt install python3.11 python3.11-venv python3-pip libportaudio2 ffmpeg
python3.11 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt
```

Example `requirements.txt`:

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

## 🎙️ Configure Audio

### 📁 Create configuration files:

```bash
echo "plughw:0,0" > /opt/script/audio_device.conf
echo "4" > /opt/script/audio_input.conf
echo "1.0" > /opt/script/mic_gain.conf
```

Adjust the values based on your setup.

---

## 📁 Prepare Directory Structure

```bash
mkdir -p /opt/script
mkdir -p /opt/sound/{responses,confirm,error,timer}
mkdir -p /opt/vosk
```

---

## 📥 Download Models

### 🧠 Vosk (Wakeword + Transcription)
- Model: `vosk-model-small-de-0.15`
- https://alphacephei.com/vosk/models

### 🗣️ Coqui TTS
```bash
# Auto-downloads on first run:
python3 -m TTS.api
```

### 🤖 GPT Model (e.g., TinyLlama or Mistral)
```bash
# Place model file here:
cp mistral-7b-instruct-v0.1.Q4_K_M.gguf /opt/
```

---

## 🧠 Start Speech System

### 🖥️ As a Service:

```ini
# /etc/systemd/system/voice_system.service
[Unit]
Description=Start voice control system (Find Audio + Wakeword)
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

Enable the service:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable voice_system
sudo systemctl start voice_system
```

---

## ✅ Testing

```bash
journalctl -u voice_system.service -f
```

Then speak: **"Alexa, what's the temperature in the living room?"**

---

## 🔒 Security

- Store your FHEM login data in `/opt/script/fhem_auth.conf`:

```ini
[FHEM]
url = http://<FHEM-IP>:8083/fhem
user = <USER>
pass = <PASSWORD>
```

---

## 📄 Files Overview

- `wakeword_niko.py`: Main system
- `gpt_temp.py`: Temperature queries
- `timer.py`: Timer functionality
- `gpt_to_fhem.py`: Send commands to FHEM
- `filter.py`: Simplify recognized text

---

## 📢 Final Note

This system runs **completely offline** – perfect for privacy, speed, and full control!

