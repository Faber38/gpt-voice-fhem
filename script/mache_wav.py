#!/usr/bin/env python3
import sys
import os
import numpy as np
import scipy.io.wavfile
import scipy.signal
from TTS.api import TTS
import argparse

# 🛠️ Argumente
parser = argparse.ArgumentParser()
parser.add_argument("text", help="Text, der gesprochen werden soll")
parser.add_argument("--max-dauer", type=float, default=None, help="Maximale Dauer in Sekunden")
parser.add_argument("--fadeout", type=float, default=0.1, help="Fade-out in Sekunden (z. B. 0.1)")
args = parser.parse_args()

# 📁 Ziel-Datei vorbereiten
output_dir = "/opt/sound"
os.makedirs(output_dir, exist_ok=True)
filename = args.text.lower().replace(" ", "_") + ".wav"
output_file = os.path.join(output_dir, filename)

print(f"🗣️ Text: {args.text}")

# 🎤 Modell laden
tts = TTS("tts_models/de/thorsten/tacotron2-DCA", progress_bar=False, gpu=True)

# 🗣️ TTS erzeugen
wav = tts.tts(args.text)
wav_array = np.array(wav)

# 🔁 Stereo, Upsample auf 48000 Hz
stereo = np.stack([wav_array, wav_array])  # [2, N]
resampled = scipy.signal.resample_poly(stereo, 48000, 22050, axis=1)

# ✂️ Maximale Länge (optional)
if args.max_dauer:
    max_len = int(48000 * args.max_dauer)
    resampled = resampled[:, :max_len]

# 📉 Fade-out (z. B. 0.1s = 4800 Samples)
fade_samples = int(48000 * args.fadeout)
if fade_samples < resampled.shape[1]:
    fade_curve = np.linspace(1.0, 0.0, fade_samples)
    for i in range(2):
        resampled[i, -fade_samples:] *= fade_curve

# 💾 Speichern
scipy.io.wavfile.write(output_file, 48000, (resampled.T * 32767).astype(np.int16))
print(f"✅ Gespeichert unter: {output_file}")
