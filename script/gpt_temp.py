#!/opt/venv/bin/python3
print("🧪 gpt_temp.py wurde aufgerufen")

import argparse
import os
import json
import requests
import numpy as np
import librosa
import re
import configparser
import sys
import sounddevice as sd
import soundfile as sf
from TTS.api import TTS

# ✅ Konfiguration
AUDIO_INDEX_FILE = "/opt/script/audio_index.conf"
TARGET_SAMPLERATE = 48000
TTS_SAMPLERATE = 22050
CONFIRM_FILE = "/tmp/fhem_confirmed"
TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TEMP_AUDIO_FILE = "/tmp/temperatur_answer.wav"
MIC_PAUSE_FLAG = "/tmp/mic_paused"

# ✅ FHEM Auth laden
config = configparser.ConfigParser()
config.read("/opt/script/fhem_auth.conf")

FHEM_URL = config.get("FHEM", "url").strip()
FHEM_USER = config.get("FHEM", "user").strip()
FHEM_PASS = config.get("FHEM", "pass").strip()

if not FHEM_URL.endswith("/fhem"):
    if not FHEM_URL.endswith("/"):
        FHEM_URL += "/"
    FHEM_URL += "fhem"

print(f"\U0001F310 Verwende FHEM-URL: {FHEM_URL}")

RAUM_DEVICE_MAP = {
    "wohnzimmer": {"device": "EnO_01A4796C", "reading": "temperature"},
    "büro": {"device": "EnO_050F4A74", "reading": "temperature"},
    "flur": {"device": "EnO_0505EC02", "reading": "temperature"},
    "schlafzimmer": {"device": "EnO_01A4D238", "reading": "temperature"},
    "bad": {"device": "EnO_05050A00", "reading": "temperature"},
    "terrasse": {"device": "HM_5FCF7A", "reading": "temperature"},
    "aussen": {"device": "HmIP_SWO_PR_001860C9991F02", "reading": "hmstate"},
}

def fix_temperature_numbers(text):
    text = re.sub(r'(\d+)\.(\d+)', r'\1 Komma \2', text)
    def replace(match):
        zahl = match.group(1)
        return f"{zahl} Grad"
    return re.sub(r'(\d+)\s*Grad', replace, text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Raumtemperatur über GPT & TTS ausgeben.")
    parser.add_argument("--text", type=str, required=True, help="Text der Temperaturabfrage")
    args = parser.parse_args()
    eingabetext = args.text.lower()

    if not os.path.exists(AUDIO_INDEX_FILE):
        print(f"❌ Audio-Index-Datei nicht gefunden: {AUDIO_INDEX_FILE}")
        sys.exit(1)
    with open(AUDIO_INDEX_FILE, "r") as f:
        AUDIO_DEVICE_INDEX = int(f.read().strip())

    print(f"🔊 Verwende Audio-Index: {AUDIO_DEVICE_INDEX}")
    print(f"🛣️ Eingabe: {eingabetext}")

    raum_erkannt = None
    for raum in RAUM_DEVICE_MAP.keys():
        if raum in eingabetext:
            raum_erkannt = raum
            break

    if not raum_erkannt:
        print("❌ Kein bekannter Raum in der Abfrage erkannt.")
        sys.exit(1)

    print(f"🌡️ Temperaturabfrage erkannt für Raum: {raum_erkannt.capitalize()}")

    device_info = RAUM_DEVICE_MAP[raum_erkannt]
    fhem_device = device_info["device"]
    fhem_reading = device_info["reading"]

    FHEM_CMD = f"jsonlist2 {fhem_device}"
    try:
        response = requests.get(
            f"{FHEM_URL}?cmd={FHEM_CMD}&XHR=1",
            auth=(FHEM_USER, FHEM_PASS),
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Fehler beim FHEM-Request oder JSON-Parsing: {e}")
        sys.exit(1)

    readings = data["Results"][0]["Readings"]
    temp_value = readings[fhem_reading]["Value"]
    print(f"✅ Temperatur-Wert ({raum_erkannt.capitalize()}): {temp_value} °C")

    temp_split = str(temp_value).split(".")
    temp_value_komma = f"{temp_split[0]} Komma {temp_split[1]}"
    print(f"✅ Temperatur ausgeschrieben: {temp_value_komma}")

    gpt_antwort = f"Im {raum_erkannt.capitalize()} beträgt die Temperatur {temp_value_komma} Grad."
    gpt_antwort = fix_temperature_numbers(gpt_antwort)
    print(f"🧐 Antwort: {gpt_antwort}")

    try:
        open(MIC_PAUSE_FLAG, "w").close()

        tts = TTS(model_name=TTS_MODEL, progress_bar=False)
        tts.to("cuda")
        print(f"🔊 Erzeuge Audio aus Antwort: {gpt_antwort}")
        wav = tts.tts(gpt_antwort, speed=0.8)
        wav_array = np.array(wav)

        max_amp = np.max(np.abs(wav_array))
        if max_amp > 0:
            wav_array = wav_array / max_amp * 0.9

        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < len(wav_array):
            wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)

        wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)
        sf.write(TEMP_AUDIO_FILE, wav_resampled, TARGET_SAMPLERATE)

        data, samplerate = sf.read(TEMP_AUDIO_FILE)
        sd.play(data, samplerate=TARGET_SAMPLERATE, device=AUDIO_DEVICE_INDEX)
        sd.wait()
    except Exception as e:
        print(f"❌ Fehler bei der Audioausgabe: {e}")
    finally:
        if os.path.exists(MIC_PAUSE_FLAG):
            os.remove(MIC_PAUSE_FLAG)
        print("✅ Wiedergabe abgeschlossen.")
        sys.exit(0)
