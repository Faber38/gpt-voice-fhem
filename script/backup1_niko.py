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
import time
from vosk import Model, KaldiRecognizer

# 🔄 Audioindex aus Datei
def get_device_index():
    try:
        with open("/opt/script/audio_index.conf", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Index: {e}")
        return None

# 🔊 Ausgabegerät aus Datei
def get_output_device():
    try:
        with open("/opt/script/audio_device.conf", "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Fehler beim Laden des Ausgabe-Geräts: {e}")
        return None

# ✅ Konfiguration
SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000
BUFFER_SIZE = 4000
TRIGGER_WORD = "niko"
RECORD_SECONDS = 16
MODEL_PATH = "/opt/vosk/vosk-de"
RESPONSES_DIR = "/opt/sound/responses"
CONFIRM_DIR = "/opt/sound/confirm"
ERROR_DIR = "/opt/sound/error"
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

# 🔊 Ausgabegerät holen
output_device = get_output_device()

# 🎧 Callback mit Resampling
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    resampled = samplerate.resample(indata, VOSK_SAMPLE_RATE / SAMPLE_RATE, 'sinc_best')
    q.put(resampled.astype('int16').tobytes())

# 🚀 Start
with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE, device=device,
                    dtype='int16', channels=1, callback=callback):
    print("🎙 Lausche auf Wakeword …")

    while True:
        data = q.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            print(f"📄 Erkannt: {result.get('text', '')}")
            if TRIGGER_WORD in result.get("text", "").lower():
                print(f"✅ Wakeword erkannt: {TRIGGER_WORD}")

                # 🔊 Zufällige Antwort abspielen
                response_files = [f for f in os.listdir(RESPONSES_DIR) if f.endswith(".wav")]
                if response_files:
                    chosen = random.choice(response_files)
                    wav_path = os.path.join(RESPONSES_DIR, chosen)
                    print(f"▶️ Spiele: {chosen}")
                    if output_device:
                        subprocess.Popen(["aplay", "-D", output_device, wav_path])
                    else:
                        print("⚠️ Kein gültiges Audio-Ausgabegerät – kann WAV nicht abspielen.")

                # 🎙 Aufnahme startet JETZT
                print("🎙 Aufnahme beginnt …")
                recorded_chunks = []
                max_chunks = int(RECORD_SECONDS * VOSK_SAMPLE_RATE / BUFFER_SIZE)

                for _ in range(max_chunks):
                    recorded_chunks.append(q.get())

                # ⏳ kleiner Puffer am Ende
                time.sleep(0.2)
                try:
                    while True:
                        recorded_chunks.append(q.get_nowait())
                except queue.Empty:
                    pass

                print("🛑 Aufnahme beendet.")

                # 💾 Speichern
                audio_data = b''.join(recorded_chunks)
                with wave.open(OUTPUT_FILE, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(VOSK_SAMPLE_RATE)
                    wf.writeframes(audio_data)

                print(f"💾 Gespeichert unter: {OUTPUT_FILE}")

                # 🧠 Transkription aus WAV
                wf = wave.open(OUTPUT_FILE, "rb")
                recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)
                print("🧠 Verarbeite gesprochene Eingabe …")
                while True:
                    chunk = wf.readframes(BUFFER_SIZE)
                    if len(chunk) == 0:
                        break
                    recognizer.AcceptWaveform(chunk)

                result = json.loads(recognizer.FinalResult())
                text = result.get("text", "")
                print(f"📝 Erkannter Text: {text}")

                # 🔄 Sende an GPT→FHEM
                print("🤖 Sende an GPT …")
                subprocess.run(["/opt/venv/bin/python", "/opt/script/gpt_to_fhem.py", text])

                # ✅ Bestätigung oder ❌ Fehler
                if os.path.exists("/tmp/fhem_confirmed"):
                    confirm_files = [f for f in os.listdir(CONFIRM_DIR) if f.endswith(".wav")]
                    if confirm_files:
                        confirm_wav = random.choice(confirm_files)
                        confirm_path = os.path.join(CONFIRM_DIR, confirm_wav)
                        print(f"▶️ Bestätigung: {confirm_wav}")
                        if output_device:
                            subprocess.Popen(["aplay", "-D", output_device, confirm_path])
                    os.remove("/tmp/fhem_confirmed")
                else:
                    error_files = [f for f in os.listdir(ERROR_DIR) if f.endswith(".wav")]
                    if error_files:
                        error_wav = random.choice(error_files)
                        error_path = os.path.join(ERROR_DIR, error_wav)
                        print(f"❌ Fehlerausgabe: {error_wav}")
                        if output_device:
                            subprocess.Popen(["aplay", "-D", output_device, error_path])
