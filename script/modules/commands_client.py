#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import difflib
from transcription import transkribiere_audio
from filter import clean_text

# Konfiguration
BASE_DIR = "/tmp"
SOUND_RESPONSE_DIR = "/opt/sound/responses"
SOUND_ERROR_DIR = "/opt/sound/error"

def apply_word_corrections(text, pfad="/opt/script/filters/radio_corrections.txt"):
    try:
        with open(pfad, "r") as f:
            for line in f:
                if "|" not in line:
                    continue
                falsch, korrekt = map(str.strip, line.strip().split("|", 1))
                if falsch and korrekt and falsch in text:
                    print(f"🔁 Ersetze '{falsch}' → '{korrekt}'")
                    text = text.replace(falsch, korrekt)
    except Exception as e:
        print(f"⚠️ Fehler beim Anwenden der Wortkorrekturen: {e}")
    return text

RADIO_STREAMS = {
    "WDR4": "http://wdr-wdr4-live.icecast.wdr.de/wdr/wdr4/live/mp3/128/stream.mp3",
    "WDR2": "https://wdr-wdr2-rheinland.icecastssl.wdr.de/wdr/wdr2/rheinland/mp3/128/stream.mp3",
    "WDR5": "http://wdr-wdr5-live.icecast.wdr.de/wdr/wdr5/live/mp3/128/stream.mp3",
    "1LIVE": "http://wdr-1live-live.icecast.wdr.de/wdr/1live/live/mp3/128/stream.mp3",
    "DLF": "https://st01.dlf.de/dlf/01/128/mp3/stream.mp3",
    "DLF_KULTUR": "https://st02.dlf.de/dlf/02/128/mp3/stream.mp3",
    "DLF_NOVA": "https://st03.dlf.de/dlf/03/128/mp3/stream.mp3",
    "BR_KLASSIK": "http://br-brklassik-live.cast.addradio.de/br/brklassik/live/mp3/128/stream.mp3",
    "BAYERN1": "http://br-bayern1-sued-live.cast.addradio.de/br/bayern1/sued/live/mp3/128/stream.mp3",
    "BAYERN3": "http://br-bayern3-live.cast.addradio.de/br/bayern3/live/mp3/128/stream.mp3"
}

def cleanup_response_files(base_dir):
    print(f"📂 DEBUG: Starte Cleanup in '{base_dir}'")
    for name in ["response.wav", "response_meta.json"]:
        path = os.path.join(base_dir, name)
        print(f"🔎 Prüfe Datei: {path}")

        if os.path.exists(path):
            print(f"📁 Datei vorhanden: {path}")
            try:
                os.remove(path)
                print(f"🧹 Datei gelöscht: {path}")
            except Exception as e:
                print(f"❌ Konnte Datei nicht löschen: {path} – Fehler: {e}")
                print(f"🛠️ Versuche Schreibrechte zu prüfen:")
                print(f"  ➜ os.access(path, os.W_OK): {os.access(path, os.W_OK)}")
                print(f"  ➜ os.stat(path).st_mode: {oct(os.stat(path).st_mode)}")
        else:
            print(f"📭 Datei nicht vorhanden: {path}")

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

def simple_tts_placeholder(text, output_path):
    """Kopiert eine Standardantwort zur Simulation von TTS"""
    import shutil, random
    try:
        files = [f for f in os.listdir(SOUND_RESPONSE_DIR) if f.endswith(".wav")]
        if not files:
            print("⚠️ Keine Antwort-WAVs vorhanden.")
            return
        src = os.path.join(SOUND_RESPONSE_DIR, random.choice(files))
        shutil.copy(src, output_path)
        print(f"📁 TTS-Platzhalter kopiert: {src} -> {output_path}")
    except Exception as e:
        print(f"❌ Fehler beim Kopieren der Antwort: {e}")

def handle_client_audio(client):
    print("💥 BEGINN von handle_client_audio() erreicht")
    print(f"📁 BASE_DIR = {BASE_DIR}")
    print(f"📄 Lade cleanup_response_files aus Datei: {__file__}")
    base_dir = f"{BASE_DIR}/{client}"
    audio_path = os.path.join(base_dir, "sende.wav")
    response_path = os.path.join(base_dir, "response.wav")
    meta_path = os.path.join(base_dir, "response_meta.json")
    cleanup_response_files(base_dir)  # 🔥 WICHTIG – ALLES ALT WEG

    if not os.path.exists(audio_path):
        print(f"❌ sende.wav fehlt unter: {audio_path}")
        return

    print(f"🎧 Verarbeite Audiodatei: {audio_path}")
    text = transkribiere_audio(audio_path)

    # 🔒 LEERER TEXT – Fehler-WAV + NOOP-META + Abbruch
    if not text:
        print("⚠️ Keine Sprache erkannt.")
        simple_tts_placeholder("Fehler bei der Spracherkennung.", response_path)

        with open(meta_path, "w") as f:
            json.dump({"action": "noop"}, f)
            print("📄 Noop-Meta geschrieben.")

        return  # ⛔⛔⛔ BRICHT AB – keine weitere Verarbeitung!

    print(f"🧹 Rohtext: {text}")
    cleaned = clean_text(text)
    print(f"🧼 Bereinigt: {cleaned}")
    cleaned = apply_word_corrections(cleaned)
    print(f"🔃 Nach Korrektur: {cleaned}")
    

    # 📻 Dynamische Radio-Erkennung
    if "radio" in cleaned or any(name.lower() in cleaned for name in RADIO_STREAMS):
        station = next((key for key in RADIO_STREAMS if key.lower() in cleaned), "WDR4")
        print(f"📻 Radio erkannt – spiele {station}")

        with open(meta_path, "w") as f:
            json.dump({
                "action": "play_radio",
                "station": station
            }, f)

        simple_tts_placeholder(f"Ich spiele {station}", response_path)
        return


    if "radio aus" in cleaned or "stopp" in cleaned:
        print("🛑 Radio-Stopp erkannt")
        with open(meta_path, "w") as f:
            json.dump({
                "action": "stop_radio"
            }, f)

        simple_tts_placeholder("Okay, ich stoppe das Radio.", response_path)
        return

    if "wetter" in cleaned:
        print(f"🌦️ Wetterbefehl erkannt: {cleaned}")
        orte_liste = lade_erlaubte_orte()
        worte = cleaned.split()
        kandidaten = [w for w in reversed(worte) if w not in ("wetter", "morgen", "heute", "wie", "wird", "das", "in")]
        ort_roh = kandidaten[0] if kandidaten else None
        ort_final = finde_bestpassenden_ort(ort_roh, orte_liste) if ort_roh else None

        if not ort_final:
            print("❌ Kein gültiger Ort erkannt – wetter_client.py wird nicht gestartet.")
            simple_tts_placeholder("Ich habe den Ort nicht verstanden.", response_path)

            with open(meta_path, "w") as f:
                json.dump({"action": "noop"}, f)
                print("📄 Noop-Meta geschrieben.")
            return

        print(f"🌍 Ort erkannt: {ort_final}")
        command = [
            "/opt/venv/bin/python3", "/opt/script/wetter_client.py",
            "--city", ort_final,
            "--output", response_path,
            "--apikey", os.environ.get("OPENWEATHER_API_KEY", "")
        ]
        print(f"🧪 Starte wetter_client.py: {' '.join(command)}")
        subprocess.run(command)
        return

    print("🤷 Keine passende Aktion erkannt – Fallback.")
    simple_tts_placeholder("Das habe ich leider nicht verstanden.", response_path)

    with open(meta_path, "w") as f:
        json.dump({"action": "noop"}, f)
        print("📄 Noop-Meta geschrieben (Fallback)")

    print(f"✅ Verarbeitung abgeschlossen für '{client}'")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True, help="Client-Name (z. B. buero)")
    args = parser.parse_args()
    handle_client_audio(args.client)
