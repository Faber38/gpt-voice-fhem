#!/opt/venv/bin/python3
import sys
import requests
import json
import os
import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
from TTS.api import TTS
from datetime import datetime

# === Konfiguration ===
API_KEY = "18544c2b1c77e05882f2ec1fe784b9a6"
TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TTS_SAMPLERATE = 22050
TARGET_SAMPLERATE = 48000
AUDIO_INDEX_FILE = "/opt/script/audio_index.conf"
MIC_PAUSE_FLAG = "/tmp/mic_paused"
AUSGABE_DATEI = "/tmp/wetter_heute.wav"

RICHTUNGEN = [
    "Norden", "Nord-Nordost", "Nordost", "Ost-Nordost", "Osten",
    "Ost-Südost", "Südost", "Süd-Südost", "Süden", "Süd-Südwest",
    "Südwest", "West-Südwest", "Westen", "West-Nordwest", "Nordwest", "Nord-Nordwest"
]

def windrichtung_text(degrees):
    index = int((degrees + 11.25) / 22.5) % 16
    richtung = RICHTUNGEN[index]
    print(f"🧭 Windrichtung aus {degrees}° → {richtung}")
    return richtung

def play_wav_file(path, audio_index):
    try:
        print(f"🔊 Spiele Datei ab: {path} auf Device Index {audio_index}")
        open(MIC_PAUSE_FLAG, "w").close()
        data, samplerate = sf.read(path)
        print(f"📈 Eingelesen: {len(data)} Samples @ {samplerate} Hz")
        if samplerate != TARGET_SAMPLERATE:
            print("🔄 Resampling erforderlich...")
            data = librosa.resample(np.array(data), orig_sr=samplerate, target_sr=TARGET_SAMPLERATE)
        sd.play(data, samplerate=TARGET_SAMPLERATE, device=audio_index)
        sd.wait()
        print("✅ Audioausgabe abgeschlossen.")
    except Exception as e:
        print(f"❌ Audiofehler: {e}")
    finally:
        if os.path.exists(MIC_PAUSE_FLAG):
            os.remove(MIC_PAUSE_FLAG)

def tts_speichern_und_abspielen(text):
    print(f"🗣️ Erzeuge TTS für: {text}")
    try:
        with open(AUDIO_INDEX_FILE) as f:
            audio_index = int(f.read().strip())
        print(f"🔧 Audioausgabe-Index: {audio_index}")
    except Exception as e:
        print(f"❌ Fehler beim Laden des Audio-Index: {e}")
        return

    try:
        tts = TTS(model_name=TTS_MODEL, progress_bar=False)
        tts.to("cuda")
        wav = tts.tts(text, speed=0.8)
        wav_array = np.array(wav)
        max_amp = np.max(np.abs(wav_array))
        if max_amp > 0:
            wav_array = wav_array / max_amp * 0.9
        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < len(wav_array):
            wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)
        wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)
        sf.write(AUSGABE_DATEI, wav_resampled, TARGET_SAMPLERATE)
        print(f"💾 Datei gespeichert: {AUSGABE_DATEI}")
        play_wav_file(AUSGABE_DATEI, audio_index)
    except Exception as e:
        print(f"❌ TTS-Fehler: {e}")

def hole_wetter(ort):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ort}&appid={API_KEY}&units=metric&lang=de"
    print(f"🌐 Wetterdaten-URL: {url}")
    print("📡 Sende Anfrage an OpenWeatherMap (2.5)...")
    response = requests.get(url)
    print(f"🔢 HTTP-Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Fehler beim Abrufen der Wetterdaten: {response.status_code}")
        return None
    try:
        data = response.json()
        print(f"🧾 Antwortinhalt: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"❌ Fehler beim Parsen der JSON-Antwort: {e}")
        return None

def hole_wetterwarnung(lat, lon):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&lang=de"
    print(f"🌐 OneCall-URL für Warnung: {url}")
    response = requests.get(url)
    print(f"🔢 HTTP-Status (Warnung): {response.status_code}")
    if response.status_code != 200:
        print(f"⚠️ Keine Wetterwarnung verfügbar (Status {response.status_code})")
        return None
    try:
        data = response.json()
        print(f"🧾 Antwortinhalt (Warnung): {json.dumps(data, indent=2)}")
        if "alerts" in data and data["alerts"]:
            warnung = data["alerts"][0]
            print(f"🚨 Warnung erkannt: {warnung['event']}")
            return f"Achtung: {warnung['event']}. {warnung['description'].split('.')[0]}."
        else:
            print("ℹ️ Keine aktuellen Warnungen enthalten.")
    except Exception as e:
        print(f"❌ Fehler beim Parsen der JSON-Antwort (Warnung): {e}")
    return None

def wetterbericht_erstellen(wetterdaten, ort):
    beschreibung = wetterdaten["weather"][0]["description"].capitalize()
    temp = round(wetterdaten["main"]["temp"])
    feels_like = round(wetterdaten["main"].get("feels_like", temp))
    wind = wetterdaten.get("wind", {})
    wind_speed = round(wind.get("speed", 0) * 3.6)
    wind_dir = windrichtung_text(wind.get("deg", 0))

    regen_text = ""
    if "rain" in wetterdaten:
        menge = wetterdaten["rain"].get("1h") or wetterdaten["rain"].get("3h")
        if menge:
            regen_text = f" Es kann {menge} Millimeter Regen geben."

    text = f"In {ort.capitalize()} ist es heute {beschreibung} bei {temp} Grad."
    if feels_like != temp:
        text += f" Gefühlt sind es {feels_like} Grad."
    if wind_speed > 0:
        text += f" Der Wind kommt aus {wind_dir} mit {wind_speed} Stundenkilometern."
    text += regen_text

    coord = wetterdaten.get("coord")
    if coord:
        warnung = hole_wetterwarnung(coord.get("lat"), coord.get("lon"))
        if warnung:
            text += f" {warnung}"
        else:
            text += " Es liegen keine Wetterwarnungen vor."
    else:
        print("⚠️ Keine Koordinaten im Wetterobjekt gefunden.")

    return text

def main():
    if len(sys.argv) < 2:
        print("Nutzung: wetter.py <optionen...>")
        sys.exit(1)

    args = [arg.lower() for arg in sys.argv[1:]]
    print(f"🧾 Argumente erkannt: {args}")

    zeitpunkt = "heute"
    ort = None

    if any("morgen" in arg for arg in args):
        zeitpunkt = "morgen"
    elif any("heute" in arg for arg in args):
        zeitpunkt = "heute"

    for arg in args:
        if arg not in ("wetter", "morgen", "heute"):
            ort = arg
            break

    if not ort:
        print("❌ Ort konnte nicht erkannt werden.")
        sys.exit(1)

    print(f"📍 Ort: {ort}")
    print(f"📆 Wetterzeitraum erkannt: {zeitpunkt}")

    if zeitpunkt == "morgen":
        wetterdaten = hole_wetter(ort)
        if not wetterdaten:
            return

        coord = wetterdaten.get("coord")
        if not coord:
            print("❌ Keine Koordinaten verfügbar für Vorhersage.")
            return

        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={coord['lat']}&lon={coord['lon']}&appid={API_KEY}&units=metric&lang=de&exclude=current,minutely,hourly,alerts"
        print(f"🌐 OneCall-URL: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen der Vorhersage: {response.status_code}")
            return
        data = response.json()
        if "daily" not in data or len(data["daily"]) < 2:
            print("❌ Keine Vorhersage für morgen gefunden.")
            return
        morgen = data["daily"][1]
        beschreibung = morgen["weather"][0]["description"].capitalize()
        temp_max = round(morgen["temp"]["max"])
        temp_min = round(morgen["temp"]["min"])
        wind_speed = round(morgen["wind_speed"] * 3.6)
        wind_deg = morgen.get("wind_deg", 0)
        wind_dir = windrichtung_text(wind_deg)

        regen_text = ""
        if "rain" in morgen:
            regen_text = f" Es kann {morgen['rain']} Millimeter Regen geben."

        text = f"In {ort.capitalize()} wird es morgen {beschreibung} bei Temperaturen zwischen {temp_min} und {temp_max} Grad."
        text += f" Der Wind kommt aus {wind_dir} mit {wind_speed} Stundenkilometern."
        text += regen_text

        warnung = hole_wetterwarnung(coord['lat'], coord['lon'])
        if warnung:
            text += f" {warnung}"
        else:
            text += " Es liegen keine Wetterwarnungen vor."

        print(f"🗣️ Wetterbericht: {text}")
        tts_speichern_und_abspielen(text)
        return

    wetterdaten = hole_wetter(ort)
    if not wetterdaten:
        return

    sprechtext = wetterbericht_erstellen(wetterdaten, ort)
    print(f"🗣️ Wetterbericht: {sprechtext}")
    tts_speichern_und_abspielen(sprechtext)

if __name__ == "__main__":
    main()
