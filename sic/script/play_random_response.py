#!/usr/bin/env python3
import os
import random
import sounddevice as sd
import soundfile as sf

# 🔧 Konfiguration
RESPONSES_DIR = "/opt/sound/responses"
INDEX_FILE = "/opt/script/audio_index.conf"

# 🔎 WAV-Dateien finden
files = [f for f in os.listdir(RESPONSES_DIR) if f.endswith(".wav")]
if not files:
    print("❌ Keine WAV-Dateien gefunden!")
    exit(1)

# 🎲 Zufällige Datei auswählen
chosen_file = os.path.join(RESPONSES_DIR, random.choice(files))
print(f"▶️ Spiele: {os.path.basename(chosen_file)}")

# 🔊 Wiedergabegerät auslesen
try:
    with open(INDEX_FILE, "r") as f:
        index = int(f.read().strip())
except Exception:
    index = None
    print("⚠️ Kein Audio-Index gefunden – Standardgerät wird verwendet.")

# ▶️ Abspielen
data, samplerate = sf.read(chosen_file)
sd.play(data, samplerate=samplerate, device=index)
sd.wait()
