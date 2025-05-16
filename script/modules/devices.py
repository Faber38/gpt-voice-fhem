import os
import wave
import contextlib


def get_output_device():
    try:
        with open("/opt/script/audio_device.conf", "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Fehler beim Laden des Ausgabe-Geräts: {e}")
        return None


def get_input_device_index():
    try:
        with open("/opt/script/audio_input.conf", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Input-Index: {e}")
        return None


def get_gain_factor():
    try:
        with open("/opt/script/mic_gain.conf", "r") as f:
            return float(f.read().strip())
    except Exception:
        print("⚠️ Kein Verstärkungsfaktor gefunden, nutze Standard 1.0")
        return 1.0


def get_wav_duration(wav_path):
    with contextlib.closing(wave.open(wav_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)
