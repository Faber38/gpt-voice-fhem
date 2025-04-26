#!/usr/bin/env python3
import sys
import requests
import os
import configparser
import subprocess

# 📄 Konfiguration
DEVICE_FILE = "/opt/script/device.txt"
UNRECOGNIZED_LOG = "/opt/script/unrecognized.log"
config = configparser.ConfigParser()
config.read("/opt/script/fhem_auth.conf")

FHEM_URL = config.get("FHEM", "url")
FHEM_USER = config.get("FHEM", "user")
FHEM_PASS = config.get("FHEM", "pass")
CONFIRM_FILE = "/tmp/fhem_confirmed"

# ✅ Eingabe prüfen
if len(sys.argv) < 2:
    print("❌ Bitte gib einen Sprachbefehl ein.")
    sys.exit(1)

# 🔠 Text direkt weiterverarbeiten – ohne erneutes Filtern
user_input = sys.argv[1].lower().strip().rstrip(".!?")
print(f"📥 Eingabe: {user_input}")

filtered = user_input  # NICHT erneut filtern!
print(f"🚫 Kein erneutes Filtern → Verwende: {filtered}")

# 📄 Datei laden
try:
    with open(DEVICE_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"❌ Fehler beim Lesen von device.txt: {e}")
    sys.exit(1)

if "hilfe" in filtered:
    print("🎧 Befehl erkannt: Hilfe anfordern")
    if "rollade" in filtered:
        help_file_path = "/opt/sound/hilfe/rolladen.wav"
        print("🎧 Hilfe zu Rollade wird abgespielt.")
    elif "licht" in filtered:
        help_file_path = "/opt/sound/hilfe/licht.wav"
        print("🎧 Hilfe zu Licht wird abgespielt.")
    else:
        print("❌ Keine spezifische Hilfe gefunden.")
        with open(UNRECOGNIZED_LOG, "a") as log:
            log.write(f"Hilfe unklar: {user_input}\n")
        sys.exit(0)

    if os.path.exists(help_file_path):
        print(f"▶️ Spiele Hilfe-Datei: {help_file_path}")
        with open("/opt/script/audio_device.conf", "r") as f:
            alsa_dev = f.read().strip()
        subprocess.Popen(["aplay", "-D", alsa_dev, help_file_path])
    else:
        print(f"❌ Hilfe-Datei nicht gefunden: {help_file_path}")
    sys.exit(0)

# Falls es kein Hilfe-Befehl war, fortfahren
print("📄 Erlaubte Kombinationen:")
matches = []
for line in lines:
    print(f" → {line}")
    parts = line.split()
    if len(parts) < 2:
        continue

    if len(parts) == 3:
        raum, geraet, aktionen = parts
    else:
        raum = ""
        geraet, aktionen = parts

    raum_opts = raum.lower().split("|") if raum else []
    geraet_opts = geraet.lower().split("|")
    aktion_opts = aktionen.lower().split("|")

    filtered_words = filtered.split()
    raum_ok = any(opt in filtered_words for opt in raum_opts) if raum_opts else True
    geraet_ok = any(opt in filtered_words for opt in geraet_opts)
    aktion_ok = any(opt in filtered_words for opt in aktion_opts)

    print(f"🔎 Prüfe: Raum={raum_opts}, Gerät={geraet_opts}, Aktion={aktion_opts}")
    print(f"   → Ergebnis: raum_ok={raum_ok}, geraet_ok={geraet_ok}, aktion_ok={aktion_ok}")

    if raum_ok and geraet_ok and aktion_ok:
        befehl = " ".join(filter(None, [raum.title(), geraet.title(), aktionen.split("|")[0].lower()]))
        matches.append(befehl)

# 🧠 Ergebnis senden
if len(matches) == 1:
    befehl = matches[0]
    print(f"💬 Erkannt: {befehl}")
    try:
        requests.get(
            f"{FHEM_URL}/fhem",
            params={"cmd": f"set GptVoiceCommand {befehl}", "XHR": "1"},
            auth=(FHEM_USER, FHEM_PASS),
            timeout=3
        )
        print("✅ an FHEM gesendet → Dummy: GptVoiceCommand")
        with open(CONFIRM_FILE, "w") as f:
            f.write("ok")
    except Exception as e:
        print(f"❌ Fehler beim Senden an FHEM: {e}")
        with open(UNRECOGNIZED_LOG, "a") as log:
            log.write(f"Sendefehler: {user_input}\n")
elif len(matches) > 1:
    print(f"❌ Mehrdeutige Treffer: {matches}")
    with open(UNRECOGNIZED_LOG, "a") as log:
        log.write(f"Mehrdeutig: {user_input}\n")
else:
    print("❌ Keine passende Kombination gefunden.")
    with open(UNRECOGNIZED_LOG, "a") as log:
        log.write(f"Nicht erkannt: {user_input}\n")
