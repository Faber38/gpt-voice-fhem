#!/usr/bin/env python3
import os
import sys
import json
import requests
import numpy as np
import soundfile as sf
import librosa
from TTS.api import TTS

# --- Konfiguration ---
TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TTS_SAMPLERATE = 22050
TARGET_SAMPLERATE = 48000

def windrichtung_text(degrees):
    richtungen = [
        "Norden", "Nord-Nordost", "Nordost", "Ost-Nordost", "Osten",
        "Ost-Südost", "Südost", "Süd-Südost", "Süden", "Süd-Südwest",
        "Südwest", "West-Südwest", "Westen", "West-Nordwest", "Nordwest", "Nord-Nordwest"
    ]
    index = int((degrees + 11.25) / 22.5) % 16
    return richtungen[index]

def tts_speichern(text, ausgabe_datei):
    print(f"🗣️ (Client) Erzeuge TTS für: {text}")
    try:
        tts = TTS(model_name=TTS_MODEL, progress_bar=False)
        tts.to("cuda")
        wav = tts.tts(text, speed=0.85)
        wav_array = np.array(wav)
        max_amp = np.max(np.abs(wav_array))
        if max_amp > 0:
            wav_array = wav_array / max_amp * 0.9
        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < len(wav_array):
            wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)
        wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)
        sf.write(ausgabe_datei, wav_resampled, TARGET_SAMPLERATE)
        print(f"💾 Gespeichert unter: {ausgabe_datei}")
    except Exception as e:
        print(f"❌ Fehler bei TTS: {e}")

def wetterbericht_erstellen(data, ort):
    beschreibung = data["weather"][0]["description"].capitalize()
    temp = round(data["main"]["temp"])
    feels_like = round(data["main"].get("feels_like", temp))
    wind_speed = round(data.get("wind", {}).get("speed", 0) * 3.6)
    wind_dir = windrichtung_text(data.get("wind", {}).get("deg", 0))

    text = f"In {ort.capitalize()} ist es {beschreibung} bei {temp} Grad."
    if feels_like != temp:
        text += f" Gefühlt sind es {feels_like} Grad."
    if wind_speed > 0:
        text += f" Der Wind kommt aus {wind_dir} mit {wind_speed} Stundenkilometern."
    return text

def hole_wetterdaten(ort, api_key):
    print(f"🌐 Hole Wetterdaten für: {ort}")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ort}&appid={api_key}&units=metric&lang=de"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        print(f"❌ Fehler beim Senden der Anfrage: {e}")
        return None

def main():
    if len(sys.argv) < 4:
        print("❌ Nutzung: wetter_client.py --city <stadt> --output <pfad> --apikey <key>")
        sys.exit(1)

    args = sys.argv[1:]
    try:
        city = args[args.index("--city") + 1]
        output = args[args.index("--output") + 1]
        apikey = args[args.index("--apikey") + 1]
    except Exception as e:
        print(f"❌ Fehler beim Verarbeiten der Argumente: {e}")
        sys.exit(1)

    wetter = hole_wetterdaten(city, apikey)
    if not wetter:
        return

    sprechtext = wetterbericht_erstellen(wetter, city)
    print(f"📄 Wettertext: {sprechtext}")
    tts_speichern(sprechtext, output)

if __name__ == "__main__":
    main()
