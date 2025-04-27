#!/usr/bin/env python3
import queue
import sys
import sounddevice as sd
import subprocess
import json
import os
import wave
import contextlib
import numpy as np
import samplerate
import random
import time
from vosk import Model, KaldiRecognizer
from filter import clean_text

def get_output_device():
    try:
        with open("/opt/script/audio_device.conf", "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Fehler beim Laden des Ausgabe-Geräts: {e}")
        return None

def get_input_device_index():
    try:
        with open("/opt/script/audio_input.conf", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Input-Index: {e}")
        return None

def get_gain_factor():
    try:
        with open("/opt/script/mic_gain.conf", "r") as f:
            return float(f.read().strip())
    except Exception as e:
        print(f"⚠️ Kein Verstärkungsfaktor gefunden, nutze Standard 1.0")
        return 1.0

def get_wav_duration(wav_path):
    with contextlib.closing(wave.open(wav_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration

SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000
BUFFER_SIZE = 2048
TRIGGER_WORD = "alexa"
RECORD_SECONDS = 14
MODEL_PATH = "/opt/vosk/vosk-de"
RESPONSES_DIR = "/opt/sound/responses"
CONFIRM_DIR = "/opt/sound/confirm"
ERROR_DIR = "/opt/sound/error"
OUTPUT_FILE = "/tmp/command.wav"

PLAUDER_MODUS = False
LETZTER_SPRECHZEITPUNKT = 0
PLAUDER_TIMEOUT = 30

q = queue.Queue()

print("🎧 Starte Wakeword-Erkennung … (sage 'alexa')")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)

input_device = get_input_device_index()
output_device = get_output_device()
gain_factor = get_gain_factor()

if input_device is None:
    print("❌ Kein Input-Audio-Gerät gefunden.")
    sys.exit(1)

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    mono_data = np.mean(indata, axis=1, keepdims=True)
    resampled = samplerate.resample(mono_data, VOSK_SAMPLE_RATE / SAMPLE_RATE, "sinc_best")
    q.put(resampled.astype("int16").tobytes())

stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    blocksize=BUFFER_SIZE,
    device=input_device,
    dtype="int16",
    channels=2,
    callback=callback,
)
stream.start()
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

            stream.stop()
            print("🔇 Mikrofon gestoppt …")

            response_files = [f for f in os.listdir(RESPONSES_DIR) if f.endswith(".wav")]
            if response_files:
                chosen = random.choice(response_files)
                wav_path = os.path.join(RESPONSES_DIR, chosen)
                print(f"▶️ Spiele: {chosen}")
                if output_device:
                    subprocess.Popen(["aplay", "-D", output_device, wav_path])
                    duration = get_wav_duration(wav_path)
                    print(f"🎵 WAV-Dauer: {duration:.2f} Sekunden")
                    time.sleep(duration + 0.5)
                else:
                    print("⚠️ Kein gültiges Audio-Ausgabegerät – kann WAV nicht abspielen.")

            stream.start()
            print("🎙 Mikrofon wieder aktiv – Aufnahme beginnt …")

            LETZTER_SPRECHZEITPUNKT = time.time()
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
            audio_data = b"".join(recorded_chunks)

            print(f"🎚 Verstärke Aufnahme um Faktor {gain_factor} …")
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            audio_np = np.clip(audio_np * gain_factor, -32768, 32767).astype(np.int16)
            amplified_audio_data = audio_np.tobytes()

            with wave.open(OUTPUT_FILE, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(VOSK_SAMPLE_RATE)
                wf.writeframes(amplified_audio_data)

            print(f"💾 Gespeichert unter: {OUTPUT_FILE}")

            print("🧠 Verarbeite gesprochene Eingabe mit Whisper (Deutsch) …")
            try:
                subprocess.run(
                    [
                        "/opt/whisper.cpp/build/bin/whisper-cli",
                        "-m",
                        "/opt/whisper.cpp/models/ggml-small.bin",
                        "-f",
                        OUTPUT_FILE,
                        "-otxt",
                        "-l",
                        "de",
                    ]
                )
                with open("/tmp/command.wav.txt", "r", encoding="utf-8") as f:
                    text = f.read().strip()
                print(f"📝 Erkannter Text (Whisper): {repr(text)}")
            except Exception as e:
                print(f"❌ Fehler bei Whisper-Transkription: {e}")
                text = ""

            if not text:
                print("⚠️ Kein Text erkannt, überspringe Verarbeitung.")
                continue

            print("⚡ Starte Filter …")
            filtered_text = clean_text(text)
            print(f"🧹 Gefilterter Text: {filtered_text}")

            # 🧪 Timer-Debug:
            if "timer" in filtered_text:
                print(f"🔔 Timer-Trigger erkannt in: {filtered_text}")
            else:
                print(f"❌ Kein Timer-Trigger in: {filtered_text}")

            LETZTER_SPRECHZEITPUNKT = time.time()

            if "timer" in filtered_text:
                try:
                    parts = []
                    if "für" in filtered_text:
                        parts = filtered_text.lower().split("für")[1].strip().split(" ")
                    else:
                        parts = filtered_text.lower().replace("timer", "").strip().split(" ")

                    print(f"🔍 Timer Teile: {parts}")

                    timer_duration = int(parts[0])
                    time_unit = parts[1].strip().rstrip(".").lower()

                    erlaubte_einheiten = ["sekunden", "minuten", "stunden"]
                    if time_unit not in erlaubte_einheiten:
                        print(f"❌ Unbekannte Zeiteinheit: {time_unit}.")
                    else:
                        print(f"🔔 Timer erkannt: {timer_duration} {time_unit}")
                        subprocess.Popen(
                            [
                                "/opt/venv/bin/python",
                                "/opt/script/timer.py",
                                str(timer_duration),
                                time_unit,
                            ]
                        )
                    continue

                except Exception as e:
                    print(f"❌ Fehler bei der Timer-Erkennung: {e}")
                    continue

            if "rede mit mir" in filtered_text.lower():
                PLAUDER_MODUS = True
                subprocess.run(
                    [
                        "/opt/venv/bin/python",
                        "/opt/script/gpt_chat.py",
                        filtered_text,
                    ]
                )
                continue

            print(f"🤖 Sende an GPT … Text: '{filtered_text}'")
            try:
                cmd = f'/opt/venv/bin/python /opt/script/gpt_to_fhem.py "{filtered_text}"'
                print(f"💻 Ausführen: {cmd}")

                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                print(f"📤 GPT_to_FHEM Output: '{result.stdout.strip()}'")
                if result.stderr:
                    print(f"❌ GPT_to_FHEM Fehler: '{result.stderr.strip()}'")
            except Exception as e:
                print(f"❌ Fehler beim Start von gpt_to_fhem.py: {e}")

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
