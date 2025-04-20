#!/usr/bin/env python3
import sys
import requests
import os

# 📄 Konfiguration
DEVICE_FILE = "/opt/script/device.txt"
FHEM_URL = "http://192.168.38.80:8083"
FHEM_USER = "holger"
FHEM_PASS = "co1je2sd"
CONFIRM_FILE = "/tmp/fhem_confirmed"

# ✅ Eingabe prüfen
if len(sys.argv) < 2:
    print("❌ Bitte gib einen Sprachbefehl ein.")
    sys.exit(1)

# 🔠 Text säubern (alles klein, nur relevante Wörter)
user_input = sys.argv[1].lower()
print(f"📥 Eingabe: {user_input}")

# 🔍 Füllwörter entfernen
fuellwoerter = ["bitte", "mach", "mache", "kannst", "du", "das", "den", "die", "in", "im", "der"]
filtered = " ".join([w for w in user_input.split() if w not in fuellwoerter])
print(f"🧹 Gefiltert: {filtered}")

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

    # 🔎 Komponenten erkennen
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
        # ✅ Bestätigung schreiben
        with open(CONFIRM_FILE, "w") as f:
            f.write("ok")
    except Exception as e:
        print(f"❌ Fehler beim Senden an FHEM: {e}")
elif len(matches) > 1:
    print(f"❌ Mehrdeutige Treffer: {matches}")
else:
    print("❌ Keine passende Kombination gefunden.")
