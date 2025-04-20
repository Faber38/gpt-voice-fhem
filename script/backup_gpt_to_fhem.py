#!/usr/bin/env python3
import sys
import requests

# 📄 Konfiguration
DEVICE_FILE = "/opt/script/device.txt"
FHEM_URL = "http://192.168.38.80:8083"
FHEM_USER = "holger"
FHEM_PASS = "co1je2sd"

if len(sys.argv) < 2:
    print("❌ Bitte gib einen Sprachbefehl ein.")
    sys.exit(1)

user_input = sys.argv[1].lower()
print(f"📥 Eingabe: {user_input}")

try:
    with open(DEVICE_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"❌ Fehler beim Lesen von device.txt: {e}")
    sys.exit(1)

print("📄 Erlaubte Kombinationen:")
for line in lines:
    print(f" → {line}")

matches = []

for line in lines:
                parts = line.split()
                if len(parts) == 3:
                    raum, geraet, aktion = parts
                    prüfliste = [raum, geraet, aktion]
                elif len(parts) == 2:
                    raum = ""
                    geraet, aktion = parts
                    prüfliste = [geraet, aktion]
                else:
                    continue
            
                if all(any(opt in user_input for opt in wort.split("|")) for wort in prüfliste):
                    match = " ".join(filter(None, [raum.title(), geraet.title(), aktion.lower()]))
                    matches.append(match)

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
    except Exception as e:
        print(f"❌ Fehler beim Senden an FHEM: {e}")
elif len(matches) > 1:
    print(f"❌ Mehrdeutige Treffer: {matches}")
else:
    print("❌ Keine passende Kombination gefunden.")
