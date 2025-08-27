# Datei: modules/commands_tts_client.py

import numpy as np
import soundfile as sf
import librosa
import os
from TTS.api import TTS

TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TTS_SAMPLERATE = 22050
TARGET_SAMPLERATE = 48000

def tts_speichern_und_abspielen_client(text, zielpfad):
    print(f"🗣️ (Client) Erzeuge TTS für: {text}")
    try:
        tts = TTS(model_name=TTS_MODEL, progress_bar=False)
        tts.to("cuda")
        wav = tts.tts(text, speed=0.85)
        wav_array = np.array(wav)

        # Normalisieren
        max_amp = np.max(np.abs(wav_array))
        if max_amp > 0:
            wav_array = wav_array / max_amp * 0.9

        # Ausblenden
        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < len(wav_array):
            wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)

        # Resampling
        wav_resampled = librosa.resample(
            wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE
        )

        # Speichern
        sf.write(zielpfad, wav_resampled, TARGET_SAMPLERATE)
        print(f"💾 Gespeichert unter: {zielpfad}")

    except Exception as e:
        print(f"❌ Fehler bei TTS für Client-Datei: {e}")
