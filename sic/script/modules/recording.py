import wave
import os
import time
import numpy as np
import queue
import sounddevice as sd
import contextlib
import samplerate

def record_and_save_audio(q: queue.Queue, output_file: str, gain_factor: float, vosk_sample_rate: int = 16000, buffer_size: int = 2048, record_seconds: int = 14):
    print("🎙️ Starte Aufnahme …")
    recorded_chunks = []
    max_chunks = int(record_seconds * vosk_sample_rate / buffer_size)

    for _ in range(max_chunks):
        recorded_chunks.append(q.get())

    time.sleep(0.2)
    try:
        while True:
            recorded_chunks.append(q.get_nowait())
    except queue.Empty:
        pass

    print("🔕 Aufnahme beendet.")
    audio_data = b"".join(recorded_chunks)

    print(f"🌺 Verstärke Aufnahme um Faktor {gain_factor} …")
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    audio_np = np.clip(audio_np * gain_factor, -32768, 32767).astype(np.int16)
    amplified_audio_data = audio_np.tobytes()

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(vosk_sample_rate)
        wf.writeframes(amplified_audio_data)

    print(f"📂 Gespeichert unter: {output_file}")
