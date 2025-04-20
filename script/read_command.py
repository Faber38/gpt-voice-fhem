#!/usr/bin/env python3
import wave
import json
from vosk import Model, KaldiRecognizer

# 📁 Pfad zur WAV-Datei
AUDIO_FILE = "/tmp/command.wav"
MODEL_PATH = "/opt/vosk/vosk-de"
SAMPLE_RATE = 16000  # Entspricht VOSK_SAMPLE_RATE

# 🎧 Lade Vosk-Modell
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
recognizer.SetWords(True)

# 📖 WAV-Datei öffnen und verarbeiten
with wave.open(AUDIO_FILE, "rb") as wf:
    print("🧠 Verarbeite Datei …")
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        recognizer.AcceptWaveform(data)

# 📝 Ergebnis ausgeben
result = json.loads(recognizer.FinalResult())
text = result.get("text", "")
print(f"📄 Vollständiger erkannter Text:\n{text}")
