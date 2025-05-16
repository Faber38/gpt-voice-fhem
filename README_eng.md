
# 📢 Offline Voice Control for FHEM (Home Automation)

Welcome to my **local voice assistant** for home automation – featuring **wake word detection**, **speech transcription**, **GPT-based command parsing**, and **FHEM integration**. All components run **fully offline** for **fast response times** and **maximum privacy**.

---

## 🔥 Features

- **Wake Word Detection:**  
  - Listens for **"alexa"** using Vosk (German offline model)
- **Speech Transcription:**  
  - Fully local transcription using Vosk – no Whisper, no internet
- **Command Handling:**  
  - Control lights and shutters (via FHEM)
  - Ask for indoor/outdoor temperatures
  - Calendar events
  - Small talk mode ("talk to me")
- **Text-to-Speech (TTS):**  
  - Natural German output using Coqui TTS (Thorsten voice)
- **Audio Output:**  
  - Robust playback via `aplay`, audio device configurable
  - Randomized success/error responses
- **100% Offline:**  
  - No cloud, no external APIs – works completely local
- **GPU Acceleration:**  
  - CUDA support for fast local GPT inference (TinyLlama, Phi, Mistral)

---

## ⚙️ Architecture

```text
Wake Word ("alexa") → Record (8s) → Transcription (Vosk) →
→ GPT Parsing (TinyLlama / Phi) →
→ Execute Command (FHEM) →
→ Voice Response via Coqui TTS
```

---

## 🛠️ Components

| File                    | Description |
|-------------------------|-------------|
| `wakeword_niko.py`      | Main loop: wake word → record → process |
| `gpt_to_fhem.py`        | Parses GPT output and triggers FHEM action |
| `filter.py`             | Cleans input text (e.g., "turn on the bathroom light") |
| `play_random_response.py` | Plays random confirmation messages |
| `play_random_error.py`    | Plays random error messages |
| `wetter.py`             | Weather info (via online API, then TTS) |
| `frage.py`              | General question answering (offline GPT) |
| `audio_device.conf`     | Config file for ALSA audio device (e.g. `hw:CARD=S3,DEV=0`) |

---

## 🔉 Sound Folder Structure

```text
/opt/sound/
 ├── responses/    → Random replies after wake word
 ├── confirm/      → Success responses ("done", etc.)
 ├── error/        → Error messages
 ├── timer/        → Alarm and timer sounds
```

---

## 🧰 Requirements

- **Python 3.11**
- Python packages: `vosk`, `sounddevice`, `numpy`, `librosa`, `samplerate`
- Local inference: `llama-cpp-python`, `TTS` (Coqui)
- Optional: CUDA (for local GPT & TTS acceleration)

Install using `venv` (recommended):

```bash
python3 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt
```

---

## 🏁 Getting Started

1. Start the system:

```bash
/opt/script/start_voice_system.sh
```

(This can also be launched via `voice_system.service` systemd unit.)

2. Say something like:  
**"Alexa, turn on the light in the living room"**  
→ The system will respond immediately – **fully local**.

---

## 📦 Project Structure

```text
/opt/
 ├── script/
 │    ├── wakeword_niko.py
 │    ├── gpt_to_fhem.py
 │    ├── filter.py
 │    ├── wetter.py
 │    ├── frage.py
 │    ├── play_random_response.py
 │    ├── play_random_error.py
 │    └── audio_device.conf
 ├── sound/
 │    ├── responses/
 │    ├── confirm/
 │    ├── error/
 │    └── timer/
 ├── venv/
 ├── vosk/
 │    └── vosk-de/
 ├── models/
 │    └── phi-2.Q4_K_M.gguf
```

---

## ✅ To-Do

- [x] Stabilize wake word ("alexa") with Vosk
- [x] Local GPT prompt parsing
- [x] FHEM integration complete
- [x] Coqui TTS response system
- [ ] Add system status queries (CPU, RAM)
- [ ] Add web interface for Hotspot/MAC whitelist management

---

## 👤 Author

Project by **Faber38**  
→ Local voice assistant for FHEM home automation, based on Vosk, Coqui TTS and llama-cpp  
→ Runs on **Debian VM (Proxmox)** with **CUDA-accelerated models**

---

# 🚀 Enjoy building and expanding your own local voice control system!
