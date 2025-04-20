#!/bin/bash

OUT_ALSA="/opt/script/audio_device.conf"
OUT_INDEX="/opt/script/audio_index.conf"
TARGET_NAME="PowerConf S3"

# Ausgabe leeren
echo -n "" > "$OUT_ALSA"
echo -n "" > "$OUT_INDEX"

# Suche Zeile mit PowerConf S3
line=$(arecord -l | grep -i "$TARGET_NAME")

if [[ -z "$line" ]]; then
    echo "❌ Gerät '$TARGET_NAME' nicht gefunden." > "$OUT_ALSA"
    exit 1
fi

# Karte und Gerät aus deutscher Zeile extrahieren
card=$(echo "$line" | grep -oP 'Karte \K[0-9]+')
device=$(echo "$line" | grep -oP 'Gerät \K[0-9]+')

if [[ -z "$card" || -z "$device" ]]; then
    echo "❌ Karte oder Gerät nicht erkannt." > "$OUT_ALSA"
    exit 2
fi

alsa_dev="plughw:${card},${device}"
echo "$alsa_dev" > "$OUT_ALSA"
echo "✅ Mikrofon erkannt (ALSA): $alsa_dev"

# Jetzt den Index für Python herausfinden – über dein venv!
index=$(/opt/venv/bin/python3 -c "
import sounddevice as sd
devices = sd.query_devices()
for i, d in enumerate(devices):
    if '$TARGET_NAME' in d['name'] and d['max_input_channels'] > 0:
        print(i)
        break
")

if [[ -z "$index" ]]; then
    echo "❌ Sounddevice-Index nicht gefunden."
    exit 3
fi

echo "$index" > "$OUT_INDEX"
echo "✅ Mikrofon erkannt (Index): $index"
