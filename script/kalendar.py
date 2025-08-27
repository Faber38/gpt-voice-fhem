#!/opt/venv/bin/python3
from ics import Calendar
from datetime import datetime, timedelta
from collections import defaultdict
import os
import sys
import numpy as np
import librosa
import soundfile as sf
import subprocess
from TTS.api import TTS

# === Konfiguration ===
ICS_FILE = "/opt/kalendar/elsdorf.ics"
AUDIO_DEVICE_FILE = "/opt/script/audio_device.conf"   # statt audio_index.conf
TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TTS_SAMPLERATE = 22050
TARGET_SAMPLERATE = 48000
KEINE_TERMINE_WAV = "/opt/sound/keine_termine_im_kalender.wav"
MIC_PAUSE_FLAG = "/tmp/mic_paused"

WOCHENTAG_MAP = {
    "Monday": "Montag", "Tuesday": "Dienstag", "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag", "Friday": "Freitag", "Saturday": "Samstag", "Sunday": "Sonntag"
}

def lese_alsa_device():
    try:
        with open(AUDIO_DEVICE_FILE, "r") as f:
            dev = f.read().strip()
            return dev if dev else "default"
    except Exception:
        return "default"

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
        start_datum = heute + timedelta(days=1) if datetime.now().hour >= 12 else heute
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
    ordering = list(WOCHENTAG_MAP.values())
    for tag in sorted(gruppiert.keys(), key=lambda d: ordering.index(d) if d in ordering else 99):
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
    return datetime.fromtimestamp(t).date() == datetime.now().date()

def play_wav_with_aplay(path):
    dev = lese_alsa_device()
    try:
        open(MIC_PAUSE_FLAG, "w").close()
        subprocess.run(["aplay", "-D", dev, "-q", path], check=False)
        print(f"✅ Audio abgespielt (aplay): {path}")
    except Exception as e:
        print(f"❌ Fehler bei Audioausgabe (aplay): {e}")
    finally:
        if os.path.exists(MIC_PAUSE_FLAG):
            os.remove(MIC_PAUSE_FLAG)

def tts_speichern_und_abspielen(text, argument):
    wav_datei = f"/tmp/kalendar_{argument}.wav"

    if ist_heute(wav_datei):
        print(f"📁 Verwende gecachte Datei: {wav_datei}")
        play_wav_with_aplay(wav_datei)
        return

    try:
        print(f"🧠 Erzeuge TTS für Kalendereintrag: {text}")
        tts = TTS(model_name=TTS_MODEL, progress_bar=False)
        try:
            tts.to("cuda")
        except Exception:
            tts.to("cpu")

        # TTS → 22.05 kHz float
        wav = tts.tts(text)
        wav_array = np.asarray(wav, dtype=np.float32)

        # Pegel begrenzen
        max_amp = float(np.max(np.abs(wav_array))) if wav_array.size else 0.0
        if max_amp > 0:
            wav_array = wav_array / max_amp * 0.9

        # Fade-out (300 ms)
        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < wav_array.shape[0]:
            wav_array[-fade_duration:] *= np.linspace(1.0, 0.0, fade_duration, dtype=np.float32)

        # Resample → 48 kHz
        if TTS_SAMPLERATE != TARGET_SAMPLERATE:
            wav_array = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)

        # 16-bit PCM speichern (max. ALSA-Kompatibilität)
        sf.write(wav_datei, wav_array, TARGET_SAMPLERATE, subtype="PCM_16")
        print(f"💾 Gespeichert: {wav_datei}")

        play_wav_with_aplay(wav_datei)
    except Exception as e:
        print(f"❌ Fehler beim TTS oder Schreiben/Abspielen: {e}")

def main():
    if len(sys.argv) < 2:
        print("❌ Nutzung: kalendar.py [heute|morgen|woche|YYYY-MM-DD]")
        sys.exit(1)

    argument = sys.argv[1].lower()

    if argument == "heute" and datetime.now().hour >= 12:
        print("🕛 Nach 12 Uhr – 'heute' wird übersprungen.")
        if os.path.exists(KEINE_TERMINE_WAV):
            play_wav_with_aplay(KEINE_TERMINE_WAV)
        return

    kalender = lade_kalender(ICS_FILE)
    start, ende = zeitraum_von_argument(argument)
    eintraege = finde_termine(kalender, start, ende)

    if eintraege:
        print("📆 Kalendereinträge:")
        for zeile in eintraege:
            print(zeile)
        sprechtext = generiere_sprechtext(eintraege)
        tts_speichern_und_abspielen(sprechtext, argument)
    else:
        print("📭 Keine Einträge gefunden.")
        if os.path.exists(KEINE_TERMINE_WAV):
            play_wav_with_aplay(KEINE_TERMINE_WAV)

if __name__ == "__main__":
    main()
