#!/usr/bin/env python3

import argparse
import os
import json
import requests
import numpy as np
import sounddevice as sd
import librosa
import re
import soundfile as sf
import threading
import glob
import random
import configparser
from TTS.api import TTS
from llama_cpp import Llama
from scipy.signal import find_peaks

# ✅ Konfiguration
AUDIO_INDEX_FILE = "/opt/script/audio_index.conf"
TARGET_SAMPLERATE = 48000
TTS_SAMPLERATE = 22050
CONFIRM_FILE = "/tmp/fhem_confirmed"

# ✅ FHEM Auth laden
config = configparser.ConfigParser()
config.read("/opt/script/fhem_auth.conf")

FHEM_URL = config.get("FHEM", "url").strip()
FHEM_USER = config.get("FHEM", "user").strip()
FHEM_PASS = config.get("FHEM", "pass").strip()

# ✅ /fhem sicherstellen
if not FHEM_URL.endswith("/fhem"):
    if not FHEM_URL.endswith("/"):
        FHEM_URL += "/"
    FHEM_URL += "fhem"

print(f"🌐 Verwende FHEM-URL: {FHEM_URL}")

# ✅ Raum → FHEM Device Mapping
RAUM_DEVICE_MAP = {
    "wohnzimmer": {"device": "EnO_01A4796C", "reading": "temperature"},
    "büro": {"device": "EnO_050F4A74", "reading": "temperature"},
    "flur": {"device": "EnO_0505EC02", "reading": "temperature"},
    "schlafzimmer": {"device": "EnO_01A4D238", "reading": "temperature"},
    "bad": {"device": "EnO_05050A00", "reading": "temperature"},
    "terrasse": {"device": "HM_5FCF7A", "reading": "temperature"},
    "aussen": {"device": "HmIP_SWO_PR_001860C9991F02", "reading": "hmstate"},
}

# 📥 Argumente
parser = argparse.ArgumentParser(description="Raumtemperatur über GPT & TTS ausgeben.")
parser.add_argument("--text", type=str, required=True, help="Text der Temperaturabfrage")
args = parser.parse_args()
eingabetext = args.text.lower()

# 🔊 Audio-Index laden
if not os.path.exists(AUDIO_INDEX_FILE):
    print(f"❌ Audio-Index-Datei nicht gefunden: {AUDIO_INDEX_FILE}")
    exit(1)
with open(AUDIO_INDEX_FILE, "r") as f:
    AUDIO_DEVICE_INDEX = int(f.read().strip())

print(f"🔊 Verwende Audio-Index: {AUDIO_DEVICE_INDEX}")
print(f"🛣️ Eingabe: {eingabetext}")

# ✅ Raum erkennen
raum_erkannt = None
for raum in RAUM_DEVICE_MAP.keys():
    if raum in eingabetext:
        raum_erkannt = raum
        break

# ▶️ Thinking-Sound
def play_thinking_sound_async():
    try:
        thinking_files = glob.glob("/opt/sound/temperatur/*.wav")
        if not thinking_files:
            print("⚠️ Keine Thinking-Sounds gefunden.")
            return
        sound_path = random.choice(thinking_files)
        data, samplerate = sf.read(sound_path)
        sd.play(data, samplerate, device=AUDIO_DEVICE_INDEX)
        sd.wait()
        print(f"🔊 Thinking-Sound abgespielt: {sound_path}")
    except Exception as e:
        print(f"⚠️ Fehler beim Thinking-Sound: {e}")

if not raum_erkannt:
    print("❌ Kein bekannter Raum in der Abfrage erkannt.")
    exit(1)

print(f"🌡️ Temperaturabfrage erkannt für Raum: {raum_erkannt.capitalize()}")

device_info = RAUM_DEVICE_MAP[raum_erkannt]
fhem_device = device_info["device"]
fhem_reading = device_info["reading"]

# ▶️ WAV im Hintergrund abspielen
threading.Thread(target=play_thinking_sound_async).start()

# 📡 FHEM Request
FHEM_CMD = f"jsonlist2 {fhem_device}"
try:
    response = requests.get(
        f"{FHEM_URL}?cmd={FHEM_CMD}&XHR=1",
        auth=(FHEM_USER, FHEM_PASS),
        timeout=5
    )
    response.raise_for_status()
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("❌ Antwort von FHEM war kein gültiges JSON!")
        print(f"Antwort war:\n{response.text}")
        exit(1)
except requests.exceptions.RequestException as e:
    print(f"❌ Fehler beim FHEM-Request: {e}")
    exit(1)

# 📈 Temperaturwert extrahieren
readings = data["Results"][0]["Readings"]
temp_value = readings[fhem_reading]["Value"]
print(f"✅ Temperatur-Wert ({raum_erkannt.capitalize()}): {temp_value} °C")

# 🧠 GPT vorbereiten
MODEL_PATH = "/opt/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
print(f"⚙️ Lade GPT-Modell: {MODEL_PATH} mit 35 GPU-Layern...")

llm = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=35,
    n_ctx=2048,
    use_mlock=True,
    use_mmap=True
)

print("⚙️ GPT-Modell erfolgreich geladen.")

# 🔠 Temperatur auf Kommaformat bringen
temp_split = str(temp_value).split(".")
temp_value_komma = f"{temp_split[0]} Komma {temp_split[1]}"
print(f"✅ Temperatur ausgeschrieben: {temp_value_komma}")

gpt_prompt = (
    f"Die Temperatur im {raum_erkannt.capitalize()} beträgt {temp_value_komma} Grad Celsius. "
    "Formuliere eine freundliche, kurze freundliche Antwort, wie man es einem Menschen sagen würde. "
    "Beispiel: 'Im Wohnzimmer sind es angenehme 21 komma 3 Grad.'"
)
print(f"🧐 GPT-Prompt: {gpt_prompt}")

output = llm(gpt_prompt, max_tokens=100, stop=["\n"])
gpt_antwort_raw = output["choices"][0]["text"].strip()

# 📚 Satzende erkennen
for sep in ['.', '!', '?']:
    if sep in gpt_antwort_raw:
        gpt_antwort = gpt_antwort_raw.split(sep)[0].strip() + sep
        break
else:
    gpt_antwort = f"Im {raum_erkannt.capitalize()} beträgt die Temperatur {temp_value} Grad Celsius."

print(f"🧐 GPT-Antwort (vor Korrektur): {gpt_antwort}")

# 🔧 Kommazahlen korrigieren
def fix_temperature_numbers(text):
    text = re.sub(r'(\d+)\.(\d+)', r'\1 Komma \2', text)
    def replace(match):
        zahl = match.group(1)
        if f"{zahl} Komma" not in text:
            return f"{zahl} Grad"
        else:
            return f"{zahl} Grad"
    return re.sub(r'(\d+)\s*Grad', replace, text)

gpt_antwort = fix_temperature_numbers(gpt_antwort)
print(f"🧐 GPT-Antwort (nach Korrektur): {gpt_antwort}")

# 🔊 Coqui TTS ausgeben
tts = TTS("tts_models/de/thorsten/tacotron2-DCA", progress_bar=False, gpu=True)
print(f"🔊 Erzeuge Audio aus GPT-Antwort: {gpt_antwort}")
wav = tts.tts(gpt_antwort)
wav_array = np.array(wav)

max_amp = np.max(np.abs(wav_array))
if max_amp > 0:
    wav_array = wav_array / max_amp * 0.9

fade_duration = int(TTS_SAMPLERATE * 0.3)
if fade_duration < len(wav_array):
    wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)

wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)

sd.play(wav_resampled, samplerate=TARGET_SAMPLERATE, device=AUDIO_DEVICE_INDEX)
sd.wait()
print("✅ Wiedergabe abgeschlossen.")
