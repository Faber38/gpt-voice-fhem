#!/usr/bin/env python3
import argparse
import os
import numpy as np
import sounddevice as sd
import librosa  # Für Resampling
from TTS.api import TTS

# ✅ Konfiguration
AUDIO_INDEX_FILE = "/opt/script/audio_index.conf"
TARGET_SAMPLERATE = 48000  # Dein PowerConf braucht 48kHz
TTS_SAMPLERATE = 22050  # Output vom TTS-Modell

# 📥 Argumente parsen
parser = argparse.ArgumentParser(description="Text zu Sprache (GPU, Resampling auf 48kHz, numpy).")
parser.add_argument("--text", type=str, required=True, help="Der Text, der gesprochen werden soll.")
args = parser.parse_args()

text = args.text
print(f"🗣️ Text: {text}")

# 🎛️ Audio-Index laden
if not os.path.exists(AUDIO_INDEX_FILE):
    print(f"❌ Audio-Index-Datei nicht gefunden: {AUDIO_INDEX_FILE}")
    exit(1)

with open(AUDIO_INDEX_FILE, "r") as f:
    AUDIO_DEVICE_INDEX = int(f.read().strip())

print(f"🔊 Verwende Audio-Index: {AUDIO_DEVICE_INDEX}")

# 📦 TTS Modell laden (mit GPU)
tts = TTS("tts_models/de/thorsten/tacotron2-DCA", progress_bar=False, gpu=True)

# 🔊 TTS generieren
wav = tts.tts(text)
wav_array = np.array(wav)

# 🔄 Resampling von 22050 Hz → 48000 Hz
wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)

# ▶️ Direkt abspielen
try:
    sd.play(wav_resampled, samplerate=TARGET_SAMPLERATE, device=AUDIO_DEVICE_INDEX)
    sd.wait()
    print("✅ Wiedergabe abgeschlossen.")
except Exception as e:
    print(f"❌ Fehler bei der Wiedergabe: {e}")
