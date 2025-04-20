#!/usr/bin/env python3
import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
import wave
import os

# 🎙️ Aufnahmeparameter
DEVICE_INDEX_FILE = "/opt/script/audio_index.conf"
DURATION = 5  # Sekunden
SAMPLE_RATE = 48000
CHANNELS = 1
FILENAME = "/tmp/test_mic.wav"

# 🎧 Gerät laden
with open(DEVICE_INDEX_FILE, "r") as f:
    device_index = int(f.read().strip())
print(f"🎙 Aufnahme von Gerät {device_index} …")

# 🔴 Aufnahme starten
recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', device=device_index)
sd.wait()
print("🛑 Aufnahme beendet.")

# 💾 Speichern
with wave.open(FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(recording.tobytes())
print(f"✅ Gespeichert unter: {FILENAME}")

# 🛠️ Mono → Stereo
stereo = np.stack([recording.flatten(), recording.flatten()], axis=1)

# 🔁 Speichern als Stereo WAV
wavfile.write(FILENAME, SAMPLE_RATE, stereo)

# 🔊 Abspielen
print("▶️ Spiele Aufnahme ab (Stereo) …")
os.system(f"aplay -D hw:CARD=S3,DEV=0 {FILENAME}")
