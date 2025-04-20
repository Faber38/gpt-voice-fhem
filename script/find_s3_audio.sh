#!/bin/bash

OUTPUT_FILE="/opt/script/audio_device.conf"
TARGET_NAME="PowerConf S3"

# Suche Zeile mit PowerConf S3
line=$(arecord -l | grep -i "$TARGET_NAME")

if [[ -z "$line" ]]; then
    echo "❌ Gerät '$TARGET_NAME' nicht gefunden." > "$OUTPUT_FILE"
    exit 1
fi

# Karte und Gerät aus deutscher Zeile extrahieren
card=$(echo "$line" | grep -oP 'Karte \K[0-9]+')
device=$(echo "$line" | grep -oP 'Gerät \K[0-9]+')

if [[ -z "$card" || -z "$device" ]]; then
    echo "❌ Karte oder Gerät nicht erkannt." > "$OUTPUT_FILE"
    exit 2
fi

alsa_dev="plughw:${card},${device}"
echo "$alsa_dev" > "$OUTPUT_FILE"
echo "✅ Mikrofon erkannt: $alsa_dev"
