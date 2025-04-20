#!/usr/bin/env python3
import sys
import os
import numpy as np
import sounddevice as sd
import scipy.io.wavfile
from TTS.api import TTS

# ✅ Konfiguration
DEFAULT_OUTPUT = "/opt/script/ich_hoere.wav"
INDEX_FILE = "/opt/script/audio_index.conf"
SAMPLERATE = 48000  # Für PowerConf S3

# 📥 Argumente
if len(sys.argv) < 2:
    print("❌ Bitte gib einen Text an.")
    sys.exit(1)

text = sys.argv[1]
out_path = DEFAULT_OUTPUT

if "--out" in sys.argv:
    out_idx = sys.argv.index("--out") + 1
    if out_idx < len(sys.argv):
        out_path = sys.argv[out_idx]

print(f"🗣️ Text: {text}")
print(f"📁 Zieldatei: {out_path}")

# 📦 TTS Modell laden
tts = TTS("tts_models/de/thorsten/tacotron2-DCA", progress_bar=False, gpu=False)

# 🔊 Sprachausgabe generieren
wav = tts.tts(text)
wav_array = np.array(wav)

# 💾 WAV speichern
scipy.io.wavfile.write(out_path, SAMPLERATE, (wav_array * 32767).astype(np.int16))
print(f"✅ Gespeichert als: {out_path}")
