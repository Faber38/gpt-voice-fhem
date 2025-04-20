#!/usr/bin/env python3
import queue
import sys
import sounddevice as sd
import subprocess
import json
import os
import wave
import numpy as np
import samplerate
import random
from vosk import Model, KaldiRecognizer

# 🔄 Audioindex aus Datei
def get_device_index():
    try:
        with open("/opt/script/audio_index.conf", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Index: {e}")
        return None

# ✅ Konfiguration
SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000
BUFFER_SIZE = 4000
TRIGGER_WORD = "niko"
RECORD_SECONDS = 8
MODEL_PATH = "/opt/vosk/vosk-de"
RESPONSES_DIR = "/opt/sound/responses"
OUTPUT_FILE = "/tmp/command.wav"

# 📥 Queue für Resampled Audio
q = queue.Queue()

# 📦 Modell laden
print("🎧 Starte Wakeword-Erkennung … (sage 'niko')")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)

# 🎤 Gerät holen
device = get_device_index()
if device is None:
    print("❌ Kein Audio-Gerät gefunden.")
    sys.exit(1)

# 🎧 Callback mit Resampling
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    resampled = samplerate.resample(indata, VOSK_SAMPLE_RATE / SAMPLE_RATE, 'sinc_best')
    q.put(resampled.astype('int16').tobytes())

# 🚀 Start
with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE, device=device,
                    dtype='int16', channels=1, callback=callback):

    buffer_chunks = []
    max_chunks = int((VOSK_SAMPLE_RATE * RECORD_SECONDS) / BUFFER_SIZE)

    while True:
        data = q.get()
        buffer_chunks.append(data)

        # Erkenne Wakeword
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            print(f"📄 Erkannt: {result.get('text', '')}")
            if TRIGGER_WORD in result.get("text", "").lower():
                print(f"✅ Wakeword erkannt: {TRIGGER_WORD}")

                # 🔊 Random Response
                response_files = [f for f in os.listdir(RESPONSES_DIR) if f.endswith(".wav")]
                if response_files:
                    chosen = random.choice(response_files)
                    print(f"▶️ Spiele: {chosen}")
                    # 🔊 Random Response mit konfiguriertem Device abspielen
                    try:
                        with open("/opt/script/audio_device.conf") as f:
                            audio_device = f.read().strip()
                    
                        if response_files:
                            chosen = random.choice(response_files)
                            filepath = os.path.join(RESPONSES_DIR, chosen)
                            print(f"▶️ Spiele: {chosen}")
                            os.system(f"aplay -D {audio_device} {filepath}")
                    except Exception as e:
                        print(f"❌ Fehler beim Abspielen: {e}")
                    

                print("🎙 Aufnahme beginnt …")
                recorded_data = []

                for _ in range(max_chunks):
                    recorded_data.append(q.get())

                print("🛑 Aufnahme beendet.")

                # 💾 Speichern
                audio_data = b''.join(recorded_data)
                with wave.open(OUTPUT_FILE, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(VOSK_SAMPLE_RATE)
                    wf.writeframes(audio_data)

                print(f"💾 Gespeichert unter: {OUTPUT_FILE}")

                # 🎤 Danach geht’s direkt weiter mit Wakeword
