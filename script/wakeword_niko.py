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

# 🔊 Ausgabegerät aus Datei
def get_output_device():
    try:
        with open("/opt/script/audio_device.conf", "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Fehler beim Laden des Ausgabe-Geräts: {e}")
        return None

# 🎤 Eingabegeräte-Index aus Datei
def get_input_device_index():
    try:
        with open("/opt/script/audio_index.conf", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Input-Index: {e}")
        return None

# ✅ Konfiguration
SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000
BUFFER_SIZE = 4000
TRIGGER_WORD = "alexa"
RECORD_SECONDS = 16
MODEL_PATH = "/opt/vosk/vosk-de"
RESPONSES_DIR = "/opt/sound/responses"
CONFIRM_DIR = "/opt/sound/confirm"
ERROR_DIR = "/opt/sound/error"
OUTPUT_FILE = "/tmp/command.wav"

# 🆕 Plaudermodus-Variablen
PLAUDER_MODUS = False
LETZTER_SPRECHZEITPUNKT = 0
PLAUDER_TIMEOUT = 30  # Sekunden

# 📥 Queue für Resampled Audio
q = queue.Queue()

# 📦 Modell laden
print("🎧 Starte Wakeword-Erkennung … (sage 'alexa')")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)

# 🎤 Geräte holen
input_device = get_input_device_index()
output_device = get_output_device()

if input_device is None:
    print("❌ Kein Input-Audio-Gerät gefunden.")
    sys.exit(1)

# 🎧 Callback mit Resampling
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    resampled = samplerate.resample(indata, VOSK_SAMPLE_RATE / SAMPLE_RATE, 'sinc_best')
    q.put(resampled.astype('int16').tobytes())

# 🚀 Start
with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE, device=input_device,
                    dtype='int16', channels=1, callback=callback):
    print(f"🎙 Lausche auf Wakeword … (Device-Index: {input_device})")

    while True:
        if PLAUDER_MODUS and time.time() - LETZTER_SPRECHZEITPUNKT > PLAUDER_TIMEOUT:
            print("⏳ Plaudermodus automatisch beendet (Timeout).")
            PLAUDER_MODUS = False

        data = q.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            erkannter_text = result.get("text", "")
            print(f"📄 Erkannt: {erkannter_text}")

            if TRIGGER_WORD in erkannter_text.lower():
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

                LETZTER_SPRECHZEITPUNKT = time.time()
                print("🎙 Aufnahme beginnt …")
                recorded_chunks = []
                max_chunks = int(RECORD_SECONDS * VOSK_SAMPLE_RATE / BUFFER_SIZE)

                for _ in range(max_chunks):
                    recorded_chunks.append(q.get())

                time.sleep(0.2)
                try:
                    while True:
                        recorded_chunks.append(q.get_nowait())
                except queue.Empty:
                    pass

                print("🛑 Aufnahme beendet.")
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

                LETZTER_SPRECHZEITPUNKT = time.time()

                if "rede mit mir" in text.lower():
                    print("🗣️ Plaudermodus aktiviert.")
                    PLAUDER_MODUS = True
                    subprocess.run(["/opt/venv/bin/python", "/opt/script/gpt_chat.py", "Okay, ich höre zu."])
                    continue

                if PLAUDER_MODUS:
                    subprocess.run(["/opt/venv/bin/python", "/opt/script/gpt_chat.py", text])
                    continue

                print("🤖 Sende an GPT …")
                subprocess.run(["/opt/venv/bin/python", "/opt/script/gpt_to_fhem.py", text])

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
