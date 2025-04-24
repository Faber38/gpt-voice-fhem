#!/opt/venv/bin/python
import sys
import subprocess
import wave
import queue
import sounddevice as sd
import time
import json
import samplerate
from vosk import Model, KaldiRecognizer
from llama_cpp import Llama

# 🔄 Eingabegeräte-Index aus Datei (für sounddevice)
def get_input_device_index():
    try:
        with open("/opt/script/audio_index.conf", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Input-Index: {e}")
        return None

# 🔊 Ausgabegerät aus Datei (für aplay)
def get_output_device():
    try:
        with open("/opt/script/audio_device.conf", "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Fehler beim Laden des Ausgabe-Geräts: {e}")
        return None

# ✅ Konfiguration
SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000
BUFFER_SIZE = 4000
RECORD_SECONDS = 10
MODEL_PATH = "/opt/vosk/vosk-de"
OUTPUT_FILE = "/tmp/chat_command.wav"
PLAUDER_TIMEOUT = 30  # Sekunden

# 🧠 GPT initialisieren
llm = Llama(model_path="/opt/phi-2.Q4_K_M.gguf", n_ctx=2048)

# 🎧 Queue für Audio
q = queue.Queue()

# 📥 Eingabegerät holen
input_device = get_input_device_index()
output_device = get_output_device()

if input_device is None:
    print("❌ Kein Input-Audio-Gerät gefunden.")
    sys.exit(1)

# 🎛️ Geräteinfo & Kanäle ermitteln
info = sd.query_devices(input_device, 'input')
channels = info['max_input_channels']
print(f"🎛️ Eingabekanäle erkannt: {channels}")

# 📦 Vosk Modell laden
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)

# 🧠 GPT Antwort generieren
def gpt_antwort(text):
    prompt = f"Antworte freundlich auf Deutsch auf: {text}\n"
    output = llm(prompt, max_tokens=100, stop=["\n", "User:"], echo=False)
    antwort = output['choices'][0]['text'].strip()
    print(f"🧠 GPT-Antwort: {antwort}")
    return antwort

# 🔊 TTS Antwort ausgeben
def tts_ausgabe(text):
    subprocess.run(["/opt/venv/bin/python", "/opt/script/coqui_tts.py", text])

# 🎧 Callback mit Resampling
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    mono_data = indata[:, 0]  # Nur linken Kanal für Vosk
    resampled = samplerate.resample(mono_data, VOSK_SAMPLE_RATE / SAMPLE_RATE, 'sinc_best')
    q.put(resampled.astype('int16').tobytes())

# 🗣️ Erste Antwort: „Okay, ich höre zu.“
tts_ausgabe("Okay, ich höre zu.")
LETZTER_SPRECHZEITPUNKT = time.time()

# 🚀 Plauder-Loop starten
with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE, device=input_device,
                    dtype='int16', channels=channels, callback=callback):
    print(f"🗣️ Plaudermodus gestartet mit Gerät {input_device} …")

    while True:
        if time.time() - LETZTER_SPRECHZEITPUNKT > PLAUDER_TIMEOUT:
            print("⏳ Plaudermodus automatisch beendet (Timeout).")
            break

        print("🎙 Ich höre dir zu …")
        recorded_chunks = []
        max_chunks = int(RECORD_SECONDS * VOSK_SAMPLE_RATE / BUFFER_SIZE)

        for _ in range(max_chunks):
            recorded_chunks.append(q.get())

        time.sleep(0.2)
        try:
            while True:
                recorded_chunks.append(q.get_nowait())
        except queue.Empty:
            pass

        audio_data = b''.join(recorded_chunks)
        with wave.open(OUTPUT_FILE, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(VOSK_SAMPLE_RATE)
            wf.writeframes(audio_data)

        print(f"💾 Gespeichert unter: {OUTPUT_FILE}")

        # 🧠 Transkription
        wf = wave.open(OUTPUT_FILE, "rb")
        recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)
        while True:
            chunk = wf.readframes(BUFFER_SIZE)
            if len(chunk) == 0:
                break
            recognizer.AcceptWaveform(chunk)
        result = json.loads(recognizer.FinalResult())
        plauder_text = result.get("text", "")
        print(f"📝 Erkannter Text (Plaudermodus): {plauder_text}")

        if plauder_text:
            LETZTER_SPRECHZEITPUNKT = time.time()
            antwort = gpt_antwort(plauder_text)
            tts_ausgabe(antwort)
        else:
            print("⚠️ Kein Text erkannt – warte weiter …")
