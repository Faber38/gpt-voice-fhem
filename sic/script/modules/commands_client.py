#!/usr/bin/env python3
import os
import sys
import json
import subprocess

sys.path.insert(0, "/opt/script")
print("🧪 DEBUG: Starte commands_client.py")

try:
    from modules.commands_tts_client import tts_speichern_und_abspielen_client
    print("✅ DEBUG: Import von TTS-Funktion erfolgreich")
except Exception as e:
    print(f"❌ DEBUG: Fehler beim Import von TTS: {e}")
    raise

from transcription import transkribiere_audio
from filter import clean_text

# 🔄 Ortsliste & Korrektur
import difflib

def lade_erlaubte_orte(pfad="/opt/script/orte.txt"):
    try:
        with open(pfad, "r") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Fehler beim Laden der Ortsliste: {e}")
        return []

def finde_bestpassenden_ort(erkannt, erlaubte_orte):
    treffer = difflib.get_close_matches(erkannt.lower(), erlaubte_orte, n=1, cutoff=0.6)
    if treffer:
        print(f"🧠 Ort '{erkannt}' korrigiert zu '{treffer[0]}'")
        return treffer[0]
    return erkannt

# 🔑 API-Key laden
import configparser
config = configparser.ConfigParser()
config.read("/opt/script/api_keys.conf")
API_KEY = config.get("OpenWeather", "api_key").strip()

def handle_client_audio(client):
    base_dir = f"/tmp/{client}"
    audio_path = os.path.join(base_dir, "sende.wav")
    response_path = os.path.join(base_dir, "response.wav")
    meta_path = os.path.join(base_dir, "response_meta.json")

    if not os.path.exists(audio_path):
        print(f"❌ sende.wav fehlt unter: {audio_path}")
        return

    print(f"🎧 Verarbeite Audiodatei: {audio_path}")
    text = transkribiere_audio(audio_path)

    if not text:
        print("⚠️ Keine Sprache erkannt.")
        print(f"🎤 DEBUG: TTS → 'Ich konnte dich leider nicht verstehen.' → {response_path}")
        tts_speichern_und_abspielen_client("Ich konnte dich leider nicht verstehen.", response_path)
        return

    print(f"🧹 Rohtext: {text}")
    cleaned = clean_text(text)
    print(f"🧼 Bereinigt: {cleaned}")

    # --- Radio starten ---
    if "radio" in cleaned or "wdr" in cleaned:
        if "wdr4" in cleaned:
            station = "WDR4"
        elif "wdr2" in cleaned:
            station = "WDR2"
        else:
            station = "WDR4"

        print(f"📻 Radio erkannt – spiele {station}")
        with open(meta_path, "w") as f:
            json.dump({
                "action": "play_radio",
                "station": station
            }, f)

        tts_speichern_und_abspielen_client(f"Ich spiele {station}", response_path)
        return

    # --- Radio stoppen ---
    if "radio aus" in cleaned or "stopp" in cleaned:
        print("🛑 Radio-Stopp erkannt")
        with open(meta_path, "w") as f:
            json.dump({
                "action": "stop_radio"
            }, f)

        tts_speichern_und_abspielen_client("Okay, ich stoppe das Radio.", response_path)
        return

    # --- Wetter ---
    if "wetter" in cleaned:
        print(f"🌦️ Wetterbefehl erkannt: {cleaned}")
        orte_liste = lade_erlaubte_orte()
        worte = cleaned.split()
        kandidaten = [w for w in reversed(worte) if w not in ("wetter", "morgen", "heute", "wie", "wird", "das", "in")]
        ort_roh = kandidaten[0] if kandidaten else None
        ort_final = finde_bestpassenden_ort(ort_roh, orte_liste) if ort_roh else None

        if not ort_final:
            print("❌ Kein gültiger Ort erkannt – wetter_client.py wird nicht gestartet.")
            return

        print(f"🌍 Ort erkannt: {ort_final}")
        command = [
            "/opt/venv/bin/python3", "/opt/script/wetter_client.py",
            "--city", ort_final,
            "--output", response_path,
            "--apikey", API_KEY
        ]
        print(f"🧪 Starte wetter_client.py: {' '.join(command)}")
        subprocess.run(command)
        return

    # --- Fallback ---
    antwort = "Das habe ich leider nicht verstanden."
    print(f"🤷 Standardantwort: {antwort}")
    tts_speichern_und_abspielen_client(antwort, response_path)

    print(f"✅ Verarbeitung abgeschlossen für '{client}'")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True, help="Client-Name (z. B. wohnzimmer)")
    args = parser.parse_args()
    handle_client_audio(args.client)
