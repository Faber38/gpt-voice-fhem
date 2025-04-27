#!/usr/bin/env python3
import sounddevice as sd
import wave
import os
import numpy as np

# Aufnahmeparameter
device_index_file = "/opt/script/audio_input.conf"
alsa_device_file = "/opt/script/audio_device.conf"

duration = 5  # Sekunden
sample_rate = 48000
channels = 2
filename = "/tmp/test_mic.wav"

# Gerät laden
try:
    with open(device_index_file, "r") as f:
        device_index = int(f.read().strip())
    print(f"Aufnahme von Gerät (Index): {device_index} …")
except Exception as e:
    print(f"Fehler beim Laden des Eingabe-Index: {e}")
    exit(1)

try:
    with open(alsa_device_file, "r") as f:
        alsa_device = f.read().strip()
    print(f"Wiedergabe über ALSA-Gerät: {alsa_device}")
except Exception as e:
    print(f"Fehler beim Laden des Ausgabegeräts: {e}")
    exit(1)

# Geräteinfos anzeigen
try:
    info = sd.query_devices(device_index)
    print(f"Geräteinfo: {info}")
except Exception as e:
    print(f"Fehler beim Abrufen der Geräteinfo: {e}")

# Aufnahme starten
print(f"Starte Aufnahme für {duration} Sekunden mit {sample_rate} Hz, {channels} Kanälen …")
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16', device=device_index)
sd.wait()
print("Aufnahme beendet.")

# Lautstärke erhöhen
factor = 30  # Hier kannst du den Faktor anpassen
recording = np.clip(recording * factor, -32768, 32767).astype('int16')
print(f"Lautstärke um Faktor {factor} erhöht.")

# Speichern als WAV
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(channels)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(recording.tobytes())
print(f"Gespeichert unter: {filename}")

# Abspielen
print("Spiele Aufnahme ab …")
os.system(f"aplay -D {alsa_device} {filename}")

