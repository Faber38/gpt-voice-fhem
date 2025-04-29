
# 📢 Voice Control for FHEM – Local & Offline

Welcome to my **local voice control system** for smart home automation with **wakeword detection, speech transcription, GPT analysis, and FHEM control** – fully **offline** and optimized for **fast responses**!

---

## 🔥 Features

- **Wakeword Detection:**  
  - Real-time detection using Vosk (`alexa`)
- **Speech Transcription:**  
  - Fast & accurate with Faster-Whisper (`small` model, GPU-optimized)
- **Command Processing:**  
  - Temperature queries
  - Set timers
  - Chat mode ("talk to me")
  - Home automation (e.g., lights, shutters) via FHEM
- **Text-to-Speech (TTS):**  
  - Clear German speech output with Coqui TTS (Thorsten voice)
- **Audio Playback:**  
  - Reliable audio output with retry mechanism if device busy
- **Fully Local:**  
  - No cloud services required, 100% offline
- **GPU Support:**  
  - CUDA acceleration for Whisper and GPT

---

## ⚙️ Architecture

```text
Wakeword → Record Audio → Transcribe (Whisper) → 
Text Filter → Command Detection → 
Action (e.g., Timer, Temperature, FHEM) → 
Response via TTS
```

---

## 🛠️ Components

| Component            | Description |
|:---------------------|:-------------|
| `wakeword_niko.py`    | Main process: listening, recording, command evaluation |
| `gpt_temp.py`         | Temperature query and GPT-based response |
| `timer.py`            | Set and handle timers |
| `gpt_to_fhem.py`      | Send commands to FHEM |
| `filter.py`           | Filter and simplify recognized text |
| `/opt/sound/`         | WAV files for responses, timers, errors |

---

## 🧰 Requirements

- **Python 3.11**
- `vosk`, `sounddevice`, `samplerate`
- `numpy`, `librosa`, `faster-whisper`
- `TTS (coqui-ai)`, `llama-cpp-python`
- optional: CUDA for GPU acceleration

Recommended setup:

```bash
python3 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt
```

---

## 🏁 Start

1. Start the Wakeword system:

```bash
/opt/script/start_voice_system.sh
```

(Service `voice_system.service`)

2. Speak a command → The system will respond.

---

## 📦 Directory Structure

```text
/opt/
 ├── script/
 │    ├── wakeword_niko.py
 │    ├── gpt_temp.py
 │    ├── timer.py
 │    ├── gpt_to_fhem.py
 │    └── filter.py
 ├── sound/
 │    ├── responses/
 │    ├── confirm/
 │    ├── error/
 │    ├── timer/
 ├── venv/
 ├── vosk/
 ├── mistral-7b-instruct-v0.1.Q4_K_M.gguf
```

---

## 🧹 To-Do

- [x] Stabilize Wakeword detection
- [x] Separate temperature & timer logic cleanly
- [ ] Support multiple timers in parallel
- [ ] Add web interface for timer status
- [ ] Improve audio error handling

---

## 🧑‍💻 Author

Project by **Faber38**  
→ Private smart home system running **Debian VM (Proxmox)** with **local language models**.

---

# 🚀 Have fun building and customizing your own system!
