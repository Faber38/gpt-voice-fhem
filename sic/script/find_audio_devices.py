#!/usr/bin/env python3
import sounddevice as sd
import subprocess

# 📄 Ziel-Dateien
DEVICE_CONF = "/opt/script/audio_device.conf"
INDEX_CONF = "/opt/script/audio_index.conf"
INPUT_CONF = "/opt/script/audio_input.conf"

# 🔍 Suchbegriffe
OUTPUT_NAME = "PowerConf S3"
INPUT_NAME = "Wireless GO II"

# 🧹 Vorherige Inhalte löschen
for f in [DEVICE_CONF, INDEX_CONF, INPUT_CONF]:
    with open(f, "w") as file:
        file.write("")

# 🔧 ALSA Device für PowerConf S3 finden
alsa_result = subprocess.run(["arecord", "-l"], capture_output=True, text=True)
alsa_lines = alsa_result.stdout.splitlines()

alsa_device = None
for line in alsa_lines:
    if OUTPUT_NAME.lower() in line.lower():
        card = next((part for part in line.split() if "Karte" in part), None)
        device = next((part for part in line.split() if "Gerät" in part), None)
        if card and device:
            card_num = line.split("Karte ")[1].split(":")[0]
            device_num = line.split("Gerät ")[1].split(":")[0]
            alsa_device = f"plughw:{card_num},{device_num}"
            break

if alsa_device:
    with open(DEVICE_CONF, "w") as f:
        f.write(alsa_device)
    print(f"✅ PowerConf S3 ALSA: {alsa_device} → gespeichert in {DEVICE_CONF}")
else:
    print(f"❌ Kein ALSA-Gerät für {OUTPUT_NAME} gefunden.")

# 🔍 Sounddevice Indizes suchen
devices = sd.query_devices()

output_index = None
input_index = None

for i, dev in enumerate(devices):
    if OUTPUT_NAME in dev['name'] and dev['max_output_channels'] > 0:
        output_index = i
    if INPUT_NAME in dev['name'] and dev['max_input_channels'] > 0:
        input_index = i

# 💾 Ausgabe-Index speichern
if output_index is not None:
    with open(INDEX_CONF, "w") as f:
        f.write(str(output_index))
    print(f"✅ PowerConf S3 Index: {output_index} → gespeichert in {INDEX_CONF}")
else:
    print(f"❌ Kein Output-Index für {OUTPUT_NAME} gefunden.")

# 💾 Eingabe-Index speichern
if input_index is not None:
    with open(INPUT_CONF, "w") as f:
        f.write(str(input_index))
    print(f"✅ Rode Wireless GO II Index: {input_index} → gespeichert in {INPUT_CONF}")
else:
    print(f"❌ Kein Input-Index für {INPUT_NAME} gefunden.")
