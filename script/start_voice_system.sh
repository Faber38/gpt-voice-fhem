#!/bin/bash

echo "🚀 Starte Sprachsystem …"

# 1️⃣ Audio-Geräte finden
echo "🔍 Finde Audio-Geräte …"
/opt/venv/bin/python /opt/script/find_audio_devices.py
if [[ $? -ne 0 ]]; then
    echo "❌ Fehler beim Finden der Audio-Geräte."
    exit 1
fi

# 2️⃣ Wakeword starten
echo "🎧 Starte Wakeword Listener …"
/opt/venv/bin/python /opt/script/wakeword_niko.py
