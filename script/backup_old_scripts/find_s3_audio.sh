#!/bin/bash

OUT_ALSA="/opt/script/audio_device.conf"
OUT_INDEX="/opt/script/audio_index.conf"
OUT_INPUT="/opt/script/audio_input.conf"
TARGET_NAME_OUTPUT="PowerConf S3"
TARGET_NAME_INPUT="Wireless GO II RX"

# Leeren
> "$OUT_ALSA"
> "$OUT_INDEX"
> "$OUT_INPUT"

# --- OUTPUT finden (S3) ---
line_out=$(arecord -l | grep -i "$TARGET_NAME_OUTPUT")
card_out=$(echo "$line_out" | grep -oP 'Karte \K[0-9]+')
device_out=$(echo "$line_out" | grep -oP 'Gerät \K[0-9]+')
alsa_dev="plughw:${card_out},${device_out}"
echo "$alsa_dev" > "$OUT_ALSA"

index_out=$(/opt/venv/bin/python3 -c "
import sounddevice as sd
for i, d in enumerate(sd.query_devices()):
    if '$TARGET_NAME_OUTPUT' in d['name'] and d['max_output_channels'] > 0:
        print(i)
        break
")
echo "$index_out" > "$OUT_INDEX"

echo "✅ Output erkannt: $alsa_dev (Index: $index_out)"

# --- INPUT finden (RØDE) ---
line_in=$(arecord -l | grep -i "$TARGET_NAME_INPUT")
card_in=$(echo "$line_in" | grep -oP 'Karte \K[0-9]+')
device_in=$(echo "$line_in" | grep -oP 'Gerät \K[0-9]+')
alsa_input="plughw:${card_in},${device_in}"
echo "$alsa_input" > "$OUT_INPUT"

echo "✅ Input erkannt: $alsa_input"
