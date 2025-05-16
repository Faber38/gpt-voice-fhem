#!/opt/venv/bin/python3
import argparse
import os
import requests
from bs4 import BeautifulSoup
from TTS.api import TTS
import numpy as np
import soundfile as sf
import librosa
import sounddevice as sd

# Konfiguration
AUDIO_INDEX_FILE = "/opt/script/audio_index.conf"
AUSGABE_DATEI = "/tmp/frageantwort.wav"
TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TTS_SAMPLERATE = 22050
TARGET_SAMPLERATE = 48000
WOLFRAM_APPID = "DEIN_WOLFRAM_APPID"  # <- Hier ggf. ersetzen

def frage_via_duckduckgo(frage):
    try:
        url = f"https://api.duckduckgo.com/?q={frage}&format=json&no_redirect=1"
        print(f"🦆 DuckDuckGo-URL: {url}")
        res = requests.get(url, timeout=10)
        data = res.json()
        return data.get("AbstractText") or None
    except Exception as e:
        print(f"❌ DuckDuckGo-Fehler: {e}")
        return None

def frage_via_wolframalpha(frage):
    try:
        url = f"https://api.wolframalpha.com/v1/result?appid={WOLFRAM_APPID}&i={frage}"
        print(f"📐 WolframAlpha-URL: {url}")
        res = requests.get(url, timeout=10)
        return res.text if res.status_code == 200 else None
    except Exception as e:
        print(f"❌ WolframAlpha-Fehler: {e}")
        return None

def frage_via_google(frage):
    try:
        query = frage.replace(" ", "+")
        url = f"https://www.google.com/search?q={query}"
        print(f"🌍 Google-URL: {url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in ["BNeawe", "BNeawe iBp4i AP7Wnd"]:
            el = soup.find("div", class_=tag)
            if el:
                return el.text
        return None
    except Exception as e:
        print(f"❌ Google-Fehler: {e}")
        return None

def frage_via_wikipedia(direktbegriff):
    url = f"https://de.wikipedia.org/wiki/{direktbegriff}"
    print(f"📘 Wikipedia-URL: {url}")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        p = soup.find("p")
        if p:
            return p.get_text().strip()
    except Exception as e:
        return f"Fehler beim Abrufen von Wikipedia: {e}"
    return "Keine Wikipedia-Antwort gefunden."


def tts_sagen(text):
    with open(AUDIO_INDEX_FILE) as f:
        audio_index = int(f.read().strip())
    tts = TTS(TTS_MODEL, progress_bar=False)
    tts.to("cuda")
    wav = tts.tts(text, speed=0.8)
    wav_array = np.array(wav)
    if np.max(np.abs(wav_array)) > 0:
        wav_array = wav_array / np.max(np.abs(wav_array)) * 0.9
    fade_duration = int(TTS_SAMPLERATE * 0.3)
    if fade_duration < len(wav_array):
        wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)
    wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)
    sf.write(AUSGABE_DATEI, wav_resampled, TARGET_SAMPLERATE)
    sd.play(wav_resampled, samplerate=TARGET_SAMPLERATE, device=audio_index)
    sd.wait()

# Hauptlogik
parser = argparse.ArgumentParser()
parser.add_argument("--text", required=True)
args = parser.parse_args()
frage = args.text.strip()

print(f"❓ Eingabe: {frage}")

if frage.lower().startswith("frage"):
    frage_clean = frage[5:].strip(" ,:.")
    print(f"🔍 Bereinigt: {frage_clean}")
    antwort = frage_via_duckduckgo(frage_clean)
    if not antwort:
        antwort = frage_via_wolframalpha(frage_clean)
    if not antwort:
        antwort = frage_via_google(frage_clean)
    if not antwort:
        antwort = frage_via_wikipedia(frage_clean)
    if not antwort:
        antwort = "Dazu habe ich leider keine Information gefunden."
else:
    antwort = "Bitte beginne Wissensfragen mit dem Wort 'Frage'."

print(f"💬 Antwort: {antwort}")
tts_sagen(antwort)
print("🔚 frage.py abgeschlossen.")
