# Datei: modules/commands_tts.py

import numpy as np
import soundfile as sf
import librosa
import os
import sounddevice as sd
from TTS.api import TTS

TTS_MODEL = "tts_models/de/thorsten/tacotron2-DDC"
TTS_SAMPLERATE = 22050
TARGET_SAMPLERATE = 48000
AUSGABE_DATEI = "/tmp/tts_out.wav"
AUDIO_INDEX_FILE = "/opt/script/audio_index.conf"
MIC_PAUSE_FLAG = "/tmp/mic_paused"

def tts_speichern_und_abspielen(text):
    print(f"🗣️ Erzeuge TTS für: {text}")
    try:
        with open(AUDIO_INDEX_FILE) as f:
            audio_index = int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Audio-Index: {e}")
        return

    try:
        tts = TTS(model_name=TTS_MODEL, progress_bar=False)
        tts.to("cuda")
        wav = tts.tts(text, speed=0.85)
        wav_array = np.array(wav)
        max_amp = np.max(np.abs(wav_array))
        if max_amp > 0:
            wav_array = wav_array / max_amp * 0.9
        fade_duration = int(TTS_SAMPLERATE * 0.3)
        if fade_duration < len(wav_array):
            wav_array[-fade_duration:] *= np.linspace(1, 0, fade_duration)
        wav_resampled = librosa.resample(wav_array, orig_sr=TTS_SAMPLERATE, target_sr=TARGET_SAMPLERATE)
        sf.write(AUSGABE_DATEI, wav_resampled, TARGET_SAMPLERATE)
        print(f"💾 Gespeichert unter: {AUSGABE_DATEI}")
        sd.play(wav_resampled, samplerate=TARGET_SAMPLERATE, device=audio_index)
        sd.wait()
        print("✅ Audioausgabe abgeschlossen.")
    except Exception as e:
        print(f"❌ Fehler bei der Sprachausgabe: {e}")
    finally:
        if os.path.exists(MIC_PAUSE_FLAG):
            os.remove(MIC_PAUSE_FLAG)
