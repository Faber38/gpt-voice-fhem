#!/usr/bin/env python3
import sys
import requests
import os
import configparser
from filter import clean_text  # ✅ Filterfunktionen auslagern

# 📄 Konfiguration
DEVICE_FILE = "/opt/script/device.txt"
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

# 🔠 Text säubern, normalisieren und filtern
user_input = sys.argv[1].lower()
print(f"📥 Eingabe: {user_input}")
filtered = clean_text(user_input)  # ← nutzt jetzt filter.py

# 📄 Datei laden
try:
    with open(DEVICE_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"❌ Fehler beim Lesen von device.txt: {e}")
    sys.exit(1)

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

    # 🔢 Sonderfall: Aktion ist eine Zahl UND "%" ist in der Aktion erlaubt
    zahl = next((w for w in filtered_words if w.isdigit() and 0 <= int(w) <= 100), None)
    if zahl and "%" in aktion_opts:
        aktion_ok = True
        standard_aktion = zahl
    else:
        aktion_ok = any(opt in filtered_words for opt in aktion_opts)
        standard_aktion = next((opt for opt in aktion_opts if opt in filtered_words), None)

    print(f"🔎 Prüfe: Raum={raum_opts}, Gerät={geraet_opts}, Aktion={aktion_opts}")
    print(f"   → Ergebnis: raum_ok={raum_ok}, geraet_ok={geraet_ok}, aktion_ok={aktion_ok}")

    if raum_ok and geraet_ok and aktion_ok:
        standard_raum = raum.title() if raum else ""
        standard_geraet = geraet_opts[0].title()
        befehl = " ".join(filter(None, [standard_raum, standard_geraet, standard_aktion]))
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
elif len(matches) > 1:
    print(f"❌ Mehrdeutige Treffer: {matches}")
else:
    print("❌ Keine passende Kombination gefunden.")
