#!/usr/bin/env python3
import queue
import sys
import sounddevice as sd
import subprocess
import json
import numpy as np
import samplerate
from vosk import Model, KaldiRecognizer

# 🔄 Device-Index aus Datei lesen
def get_device_index():
    try:
        with open("/opt/script/audio_index.conf", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Index: {e}")
        return None

# ✅ Konfiguration
SAMPLE_RATE = 48000  # Mikrofon-Rate
VOSK_SAMPLE_RATE = 16000  # Zielrate für Vosk
BUFFER_SIZE = 4000
MODEL_PATH = "/opt/vosk/vosk-de"

# 📥 Queue zur Sprachverarbeitung
q = queue.Queue()

# 🎧 Callback für Mikrofon mit Resampling
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)

    print(f"🎤 Eingehende Rohdaten: {indata.shape}, Typ: {indata.dtype}")
    resampled = samplerate.resample(indata, VOSK_SAMPLE_RATE / SAMPLE_RATE, 'sinc_best')
    print(f"↪️  Nach Resampling: {resampled.shape}, Typ: {resampled.dtype}")

    q.put(resampled.astype('int16').tobytes())

# 📦 Modell laden
print("🎧 Starte Vosk Debug-Erkennung …")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)

# 🎤 Gerät laden
device = get_device_index()
if device is None:
    print("❌ Kein gültiges Audio-Gerät gefunden.")
    sys.exit(1)

# 🚀 Hauptloop: Nur Text ausgeben
with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE, device=device,
                    dtype='int16', channels=1, callback=callback):
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            print(f"📄 Erkannt: {text}")
