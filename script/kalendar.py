#!/opt/venv/bin/python3
from ics import Calendar
from datetime import datetime, timedelta
from collections import defaultdict
import os
import sys
import random
import glob
import numpy as np
import sounddevice as sd
import librosa
import soundfile as sf
from TTS.api import TTS

# === Konfiguration ===
ICS_FILE = "/opt/kalendar/elsdorf.ics"
AUDIO_INDEX_FILE = "/opt/script/audio_index.conf"
TTS_MODEL = "tts_models/de/thorsten/tacotron2-DCA"
TTS_SAMPLERATE = 22050
TARGET_SAMPLERATE = 48000
KEINE_TERMINE_WAV = "/opt/sound/keine_termine_im_kalender.wav"
LADE_WAV_DIR = "/opt/sound/kalendar/"

# Wochentage auf Deutsch
WOCHENTAG_MAP = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}

def lade_kalender(pfad):
    if not os.path.exists(pfad):
        print(f"Fehler: Kalenderdatei nicht gefunden: {pfad}")
        sys.exit(1)
    with open(pfad, "r", encoding="utf-8") as f:
        return Calendar(f.read())

def zeitraum_von_argument(arg):
    heute = datetime.now().date()
    if arg == "heute":
        return heute, heute
    elif arg == "morgen":
        return heute + timedelta(days=1), heute + timedelta(days=1)
    elif arg == "woche":
        if datetime.now().hour >= 12:
           start_datum = heute + timedelta(days=1)
        else:
           start_datum = heute
        return start_datum, heute + timedelta(days=6)
    else:
        try:
            datum = datetime.strptime(arg, "%Y-%m-%d").date()
            return datum, datum
        except ValueError:
            print("Ungültiges Argument. Nutze: heute, morgen, woche oder YYYY-MM-DD")
            sys.exit(1)

def finde_termine(kalender, start, ende):
    gruppiert = defaultdict(list)
    for event in kalender.events:
        event_date = event.begin.date()
        if start <= event_date <= ende:
            wochentag_en = event.begin.strftime("%A")
            wochentag_de = WOCHENTAG_MAP.get(wochentag_en, wochentag_en)
            gruppiert[wochentag_de].append(event.name)

    ausgabe = []
    for tag in sorted(gruppiert.keys(), key=lambda d: list(WOCHENTAG_MAP.values()).index(d)):
        ausgabe.append(f"{tag}:")
        for eintrag in gruppiert[tag]:
            ausgabe.append(f"- {eintrag}")
        ausgabe.append("")
    return ausgabe

def generiere_sprechtext(eintragsliste):
    sprechtext = ""
    aktueller_tag = ""
    for zeile in eintragsliste:
        zeile = zeile.strip()
        if zeile.endswith(":"):
            aktueller_tag = zeile[:-1]
        elif zeile.startswith("-") and aktueller_tag:
            eintrag = zeile.lstrip("- ").strip()
            sprechtext += f"Am {aktueller_tag} ist {eintrag}. "
    return sprechtext.strip()

def ist_heute(dateipfad):
    if not os.path.exists(dateipfad):
        return False
    t = os.path.getmtime(dateipfad)
    tag_der_datei = datetime.fromtimestamp(t).date()
    return tag_der_datei == datetime.now().date()

def play_wav_file(path, audio_index):
    try:
        data, samplerate = sf.read(path)
        print(f"🔊 Original-Samplerate: {samplerate}")
        if samplerate != TARGET_SAMPLERATE:
            data = librosa.resample(np.array(data), orig_sr=samplerate, target_sr=TARGET_SAMPLERATE)
        sd.play(data, samplerate=TARGET_SAMPLERATE, device=audio_index)
        sd.wait()
        print(f"✅ Audio erfolgreich abgespielt: {path}")
    except Exception as e:
        print(f"❌ Fehler bei Audioausgabe: {e}")

def tts_speichern_und_abspielen(text, argument):
    wav_datei = f"/tmp/kalendar_{argument}.wav"

    with open(AUDIO_INDEX_FILE) as f:
        audio_index = int(f.read().strip())

    if ist_heute(wav_datei):
        print(f"Spiele vorhandene Sprachdatei ab: {wav_datei}")
        play_wav_file(wav_datei, audio_index)
    else:
        # Zufällige Lade-Antwort abspielen
        lade_sounds = glob.glob(os.path.join(LADE_WAV_DIR, "*.wav"))
        if lade_sounds:
            zufall = random.choice(lade_sounds)
            print(f"Ladehinweis: {zufall}")
            play_wav_file(zufall, audio_index)

        print(f"Erzeuge neue Sprachdatei mit TTS für '{argument}'...")
        tts = TTS(model_name=TTS_MODEL, progress_bar=False, gpu=True)
        print(f"✅ Geladenes TTS-Modell: {tts.model_name}")
        wav = tts.tts(text)
        wav_array = np.array(wav)

        # Lautstärke normalisieren
        max_amp = np.max(np.abs(wav_array))
        if max_amp > 0:
            wav_array = wav_array / max_amp * 0.9

        # Fade-Out anwenden
        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < len(wav_array):
            wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)

        # Resampling
        wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)

        # Speichern und abspielen
        sf.write(wav_datei, wav_resampled, TARGET_SAMPLERATE)
        play_wav_file(wav_datei, audio_index)

def main():
    if len(sys.argv) < 2:
        print("Nutzung: kalendar.py [heute|morgen|woche|YYYY-MM-DD]")
        sys.exit(1)

    argument = sys.argv[1]
    
    # ⏰ Heute nach 12 Uhr? Dann Termin ignorieren
    if argument == "heute" and datetime.now().hour >= 12:
        print("🕛 Es ist nach 12 Uhr – heutige Termine werden ignoriert.")
        if os.path.exists(KEINE_TERMINE_WAV):
            with open(AUDIO_INDEX_FILE) as f:
                audio_index = int(f.read().strip())
            play_wav_file(KEINE_TERMINE_WAV, audio_index)
        return
    
    kalender = lade_kalender(ICS_FILE)
    start, ende = zeitraum_von_argument(argument)
    
    eintraege = finde_termine(kalender, start, ende)

    if eintraege:
        print("Kalendereinträge:")
        for zeile in eintraege:
            print(zeile)
        ausgabetext = generiere_sprechtext(eintraege)
        tts_speichern_und_abspielen(ausgabetext, argument)
    else:
        print("Keine Termine im angegebenen Zeitraum.")
        if os.path.exists(KEINE_TERMINE_WAV):
            with open(AUDIO_INDEX_FILE) as f:
                audio_index = int(f.read().strip())
            play_wav_file(KEINE_TERMINE_WAV, audio_index)

if __name__ == "__main__":
    main()
