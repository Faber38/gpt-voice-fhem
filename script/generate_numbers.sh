#!/bin/bash

for i in {1..60}; do
  echo "🎙️ Erstelle WAV für: $i"
  /opt/venv/bin/python /opt/script/mache_error.py "$i"
done

echo "✅ Alle Dateien erstellt!"
