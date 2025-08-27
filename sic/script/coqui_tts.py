#!/usr/bin/env python3
import sys
import subprocess
from TTS.api import TTS
import soundfile as sf
import os

# 📥 Eingabetext prüfen
if len(sys.argv) < 2:
    print("❌ Kein Text übergeben.")
    sys.exit(1)

text = sys.argv[1]
output_wav = "/tmp/tts_output.wav"

# 🎤 TTS-Modell laden (einmalig, kann dauern beim ersten Mal)
# Beispiel: ein deutsches Modell – passe an, wenn du ein anderes nutzt
tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False)
tts.to("cuda")  # Nutze jetzt deine RTX 3060!


# 🔊 Audio erzeugen
tts.tts_to_file(text=text, file_path=output_wav)

# 🎚️ Ausgabegerät holen
try:
    with open("/opt/script/audio_device.conf", "r") as f:
        output_device = f.read().strip()
except Exception as e:
    print(f"❌ Fehler beim Laden des Ausgabe-Geräts: {e}")
    output_device = None

# ▶️ WAV abspielen
if os.path.exists(output_wav):
    if output_device:
        subprocess.run(["aplay", "-D", output_device, output_wav])
    else:
        print("⚠️ Kein gültiges Audio-Ausgabegerät – kann WAV nicht abspielen.")
else:
    print("❌ Keine TTS-Ausgabe erzeugt.")
