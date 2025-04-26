#!/opt/venv/bin/python
import sys
import subprocess
from llama_cpp import Llama

# 🧠 GPT initialisieren
llm = Llama(model_path="/opt/phi-2.Q4_K_M.gguf", n_ctx=2048, n_gpu_layers=-1)

# 🔊 TTS Antwort ausgeben
def tts_ausgabe(text):
    print(f"🗣️ TTS-Ausgabe: {text}")
    subprocess.run(["/opt/venv/bin/python", "/opt/script/coqui_tts.py", text])

# ✅ Eingabetext prüfen
if len(sys.argv) < 2:
    print("❌ Bitte gib einen Test-Text ein.")
    sys.exit(1)

test_text = sys.argv[1]
print(f"📝 Test-Text: {test_text}")

# 🧠 GPT Antwort generieren
prompt = f"Antworte freundlich auf Deutsch auf: {test_text}\n"
output = llm(prompt, max_tokens=100, stop=["\n", "User:"], echo=False)
antwort = output['choices'][0]['text'].strip()
print(f"🧠 GPT-Antwort: {antwort}")

# 🔊 Antwort ausgeben
tts_ausgabe(antwort)
