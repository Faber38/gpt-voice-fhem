#!/opt/venv/bin/python3
import sys
import requests
import json
import os
import numpy as np
import soundfile as sf
import librosa
import subprocess
from TTS.api import TTS
from datetime import datetime
import configparser
from pathlib import Path

# ----------------- Konfiguration -----------------
config = configparser.ConfigParser()
config.read("/opt/script/api_keys.conf")
API_KEY = config.get("OpenWeather", "api_key").strip()

TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TTS_SAMPLERATE = 22050               # Coqui-Ausgabe
TARGET_SAMPLERATE = 48000            # Ziel für Ausgabe (PowerConf S3 ist @48k stabil)
AUDIO_DEVICE_FILE = "/opt/script/audio_device.conf"
MIC_PAUSE_FLAG = "/tmp/mic_paused"
AUSGABE_DATEI = "/tmp/wetter_heute.wav"

RICHTUNGEN = [
    "Norden", "Nord-Nordost", "Nordost", "Ost-Nordost", "Osten",
    "Ost-Südost", "Südost", "Süd-Südost", "Süden", "Süd-Südwest",
    "Südwest", "West-Südwest", "Westen", "West-Nordwest", "Nordwest", "Nord-Nordwest"
]

# ----------------- Hilfsfunktionen -----------------
def lese_alsa_device():
    try:
        dev = Path(AUDIO_DEVICE_FILE).read_text().strip()
        if dev:
            return dev
    except Exception:
        pass
    return "default"

def windrichtung_text(degrees):
    index = int((degrees + 11.25) / 22.5) % 16
    richtung = RICHTUNGEN[index]
    print(f"🧭 Windrichtung aus {degrees}° → {richtung}")
    return richtung

def play_wav_with_aplay(path):
    dev = lese_alsa_device()
    try:
        print(f"🔊 Spiele Datei ab: {path} auf ALSA-Device: {dev}")
        open(MIC_PAUSE_FLAG, "w").close()
        # -q = quiet, -D = Device (z. B. plughw:2,0)
        subprocess.run(["aplay", "-D", dev, "-q", path], check=False)
        print("✅ Audioausgabe abgeschlossen.")
    except Exception as e:
        print(f"❌ Audiofehler (aplay): {e}")
    finally:
        if os.path.exists(MIC_PAUSE_FLAG):
            os.remove(MIC_PAUSE_FLAG)

def tts_speichern_und_abspielen(text):
    print(f"🗣️ Erzeuge TTS für: {text}")
    try:
        # TTS initialisieren (GPU, falls vorhanden)
        tts = TTS(model_name=TTS_MODEL, progress_bar=False)
        try:
            tts.to("cuda")
        except Exception:
            tts.to("cpu")

        # 1) TTS → 22.05 kHz (mono)
        wav = tts.tts(text, speed=0.8)
        wav = np.asarray(wav, dtype=np.float32)

        # 2) Pegel normalisieren (Soft-Limiter)
        max_amp = float(np.max(np.abs(wav))) if wav.size else 0.0
        if max_amp > 0:
            wav = wav / max_amp * 0.9

        # 3) sanftes Fade-out (300 ms)
        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < wav.shape[0]:
            wav[-fade_duration:] *= np.linspace(1.0, 0.0, fade_duration, dtype=np.float32)

        # 4) Resampling auf 48 kHz
        if TTS_SAMPLERATE != TARGET_SAMPLERATE:
            wav = librosa.resample(wav, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)

        # 5) Als 16-bit PCM speichern (maximale ALSA-Kompatibilität)
        sf.write(AUSGABE_DATEI, wav, TARGET_SAMPLERATE, subtype="PCM_16")
        print(f"💾 Datei gespeichert: {AUSGABE_DATEI}")

        # 6) Abspielen über aplay/ALSA-Device aus Config
        play_wav_with_aplay(AUSGABE_DATEI)

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
    print(f"🔹 HTTP-Status (Warnung): {response.status_code}")
    if response.status_code != 200:
        print(f"⚠️ Keine Wetterwarnung verfügbar (Status {response.status_code})")
        return None
    try:
        data = response.json()
        print(f"🧾 Antwortinhalt (Warnung): {json.dumps(data, indent=2)}")
        if "alerts" in data and data["alerts"]:
            warnung = data["alerts"][0]
            print(f"🚨 Warnung erkannt: {warnung['event']}")
            warntext = f"Achtung: {warnung['event']}. {warnung['description'].split('.')[0]}."
            warntext = uebersetze_warnung(warntext)
            warntext = erklaere_sturmböen(warntext)
            return warntext
        else:
            print("ℹ️ Keine aktuellen Warnungen enthalten.")
    except Exception as e:
        print(f"❌ Fehler beim Parsen der JSON-Antwort (Warnung): {e}")
    return None

def uebersetze_warnung(text):
    ersetzungen = [
        ("There is a risk of wind gusts", "Es besteht die Gefahr von Sturmböen"),
        ("Achtung: wind gusts", "Achtung: Sturmböen"),
        ("wind gusts", "Sturmböen"),
        ("There is a high potential for the development of severe thunderstorms", "Es besteht eine hohe Wahrscheinlichkeit für schwere Gewitter"),
        ("Achtung: severe thunderstorms", "Achtung: schwere Gewitter"),
        ("severe thunderstorms", "schwere Gewitter"),
        ("Achtung: heavy thunderstorms with heavy rain", "Achtung: schwere Gewitter mit starkem Regen"),
        ("There is a risk of heavy thunderstorms with heavy rain", "Es besteht die Gefahr von schweren Gewittern mit starkem Regen"),
        ("heavy thunderstorms with heavy rain", "schwere Gewitter mit starkem Regen"),
        ("heavy thunderstorms with gale- or storm-force gusts, heavy rain and hail", "schwere Gewitter mit Sturmböen oder Orkanböen, starkem Regen und Hagel"),
        ("There is a risk of heavy thunderstorms with gale- or storm-force gusts, heavy rain and hail", "Es besteht die Gefahr von schweren Gewittern mit Sturmböen oder Orkanböen, starkem Regen und Hagel"),
        ("level 1 of 4", "Stufe 1 von 4"),
        ("level 2 of 4", "Stufe 2 von 4"),
        ("level 3 of 4", "Stufe 3 von 4"),
        ("level 4 of 4", "Stufe 4 von 4"),
        ("Achtung: strong heat.", "Achtung: starke Hitze."),
        ("The expected weather will bring a situation of strong heat stress.", "Das erwartete Wetter wird eine Situation mit starker Hitzebelastung bringen."),
    ]
    for englisch, deutsch in ersetzungen:
       text = text.replace(englisch, deutsch)
    return text.replace("(", "").replace(")", "")


def erklaere_sturmböen(text):
    stufen_info = {
        "Stufe 1 von 4": ("50 bis 60 Stundenkilometern", "Diese Stufe gilt als harmlos."),
        "Stufe 2 von 4": ("60 bis 80 Stundenkilometern", "Es besteht Gefahr durch herabfallende Äste oder lose Gegenstände."),
        "Stufe 3 von 4": ("80 bis 100 Stundenkilometern", "Es drohen Schäden an Bäumen, Dächern oder Fahrzeugen."),
        "Stufe 4 von 4": ("über 100 Stundenkilometern", "Es besteht akute Orkangefahr mit hohem Schadenspotenzial.")
    }
    for stufe, (kmh, bedeutung) in stufen_info.items():
        if stufe in text:
            return text + f" Das entspricht etwa {kmh}. {bedeutung}"
    return text


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

# ----------------- Main -----------------
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
