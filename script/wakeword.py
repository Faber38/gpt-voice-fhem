#!/usr/bin/env python3

import queue
import sys
import sounddevice as sd
import subprocess
import re
import json
import os
import numpy as np
import samplerate
import random
import time
import glob
import wave

from vosk import Model, KaldiRecognizer
from filter import clean_text

from modules.devices import (
    get_output_device,
    get_input_device_index,
    get_gain_factor,
    get_wav_duration
)
from modules.recording import record_and_save_audio
from modules.commands import (
    handle_timer,
    handle_kalender,
    handle_wetter,
    handle_temperature,
    handle_frage,
    play_confirmation,
    play_error
)
from modules.transcription import transkribiere_audio

# Konstanten
SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000
BUFFER_SIZE = 2048
TRIGGER_WORD = "alexa"
MODEL_PATH = "/opt/vosk/vosk-de"
RESPONSES_DIR = "/opt/sound/responses"
OUTPUT_FILE = "/tmp/command.wav"

PLAUDER_MODUS = False
LETZTER_SPRECHZEITPUNKT = 0
PLAUDER_TIMEOUT = 30

q = queue.Queue()
stream = None

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    mono_data = np.mean(indata, axis=1, keepdims=True)
    resampled = samplerate.resample(mono_data, VOSK_SAMPLE_RATE / SAMPLE_RATE, "sinc_best")
    q.put(resampled.astype("int16").tobytes())

def main():
    global stream, PLAUDER_MODUS, LETZTER_SPRECHZEITPUNKT

    print("🎧 Starte Wakeword-Erkennung … (sage 'alexa')")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)

    input_device = get_input_device_index()
    output_device = get_output_device()
    gain_factor = get_gain_factor()

    if input_device is None:
        print("❌ Kein Input-Audio-Gerät gefunden.")
        sys.exit(1)

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BUFFER_SIZE,
        device=input_device,
        dtype="int16",
        channels=2,
        callback=callback,
    )
    stream.start()
    print(f"🎹 Lausche auf Wakeword … (Device-Index: {input_device})")
    from modules import commands
    commands.set_stream(stream)

    while True:
        if PLAUDER_MODUS and time.time() - LETZTER_SPRECHZEITPUNKT > PLAUDER_TIMEOUT:
            print("⏳ Plaudermodus automatisch beendet (Timeout).")
            PLAUDER_MODUS = False

        data = q.get()
        if os.path.exists("/tmp/mic_paused"):
            continue

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            erkannter_text = result.get("text", "")
            print(f"📄 Erkannt: {erkannter_text}")

            if TRIGGER_WORD in erkannter_text.lower():
                print(f"✅ Wakeword erkannt: {TRIGGER_WORD}")

                stream.stop()
                print("🔇 Mikrofon gestoppt …")

                response_files = glob.glob(os.path.join(RESPONSES_DIR, "*.wav"))
                if response_files:
                    chosen = random.choice(response_files)
                    wav_path = os.path.join(RESPONSES_DIR, chosen)
                    print(f"▶️ Spiele: {chosen}")
                    if output_device:
                        subprocess.Popen(["aplay", "-D", output_device, wav_path])
                        duration = get_wav_duration(wav_path)
                        time.sleep(duration + 0.5)

                stream.start()
                print("🎹 Mikrofon wieder aktiv – Aufnahme beginnt …")

                LETZTER_SPRECHZEITPUNKT = time.time()
                record_and_save_audio(q, OUTPUT_FILE, gain_factor)

                text = transkribiere_audio(OUTPUT_FILE)
                if not text:
                    print("⚠️ Kein Text erkannt.")
                    continue

                print("⚡ Starte Filter …")
                filtered_text = clean_text(text)
                print(f"🩹 Gefilterter Text: {filtered_text}")

                LETZTER_SPRECHZEITPUNKT = time.time()

                if handle_timer(filtered_text, output_device):
                    continue
                if handle_kalender(filtered_text):
                    continue
                if "wetter" in filtered_text.lower():
                    if handle_wetter(filtered_text):
                        continue
                    else:
                        print("🚫 Wetterbefehl war ungültig oder Ort unbekannt – kein Fallback an GPT.")
                    continue
                if handle_temperature(filtered_text):
                    continue

                if handle_frage(filtered_text):
                    continue

                if "rede mit mir" in filtered_text.lower():
                    PLAUDER_MODUS = True
                    subprocess.run(["/opt/venv/bin/python", "/opt/script/gpt_chat.py", filtered_text])
                    continue

                print(f"🤖 Sende an GPT … Text: '{filtered_text}'")
                try:
                    cmd = f'/opt/venv/bin/python /opt/script/gpt_to_fhem.py "{filtered_text}"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    print(f"📤 GPT_to_FHEM Output: '{result.stdout.strip()}'")
                    if result.stderr:
                        print(f"❌ GPT_to_FHEM Fehler: '{result.stderr.strip()}'")
                except Exception as e:
                    print(f"❌ Fehler beim Start von gpt_to_fhem.py: {e}")

                if os.path.exists("/tmp/fhem_confirmed"):
                    play_confirmation(output_device)
                    os.remove("/tmp/fhem_confirmed")
                else:
                    play_error(output_device)

if __name__ == "__main__":
    main()
