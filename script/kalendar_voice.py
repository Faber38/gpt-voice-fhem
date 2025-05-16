#!/opt/venv/bin/python3
import sys
import subprocess
import requests

# === Modellkonfiguration ===
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"

# === Prompt-Vorlage ===
def baue_prompt(eingabe):
    return (
        "Du bist ein Assistent zur Kalendereingabe.\n"
        "Erkenne aus dem folgenden Satz den Zeitraum (heute, morgen, woche oder ein Datum im Format YYYY-MM-DD).\n"
        "Gib nur eines dieser vier Formate exakt zurück – keine Erklärung, keine Begrüßung.\n"
        f"Satz: {eingabe}"
    )

# === Nutzereingabe prüfen ===
if len(sys.argv) < 2:
    print("❌ Bitte gib eine Spracheingabe an, z. B. 'Was habe ich morgen vor?'")
    sys.exit(1)

nutzertext = sys.argv[1]

# === Prompt senden ===
prompt = baue_prompt(nutzertext)
antwort = requests.post(OLLAMA_URL, json={
    "model": OLLAMA_MODEL,
    "prompt": prompt,
    "stream": False
})

# === Antwort auslesen ===
try:
    antwort_json = antwort.json()
    zeitraum = antwort_json.get("response", "").strip().lower()
    print(f"🧠 Erkannter Zeitraum: {zeitraum}")
except Exception as e:
    print(f"❌ Fehler bei Verarbeitung der Ollama-Antwort: {e}")
    sys.exit(1)

# === Aufruf von kalendar.py mit erkanntem Zeitraum ===
kalendar_script = "/opt/kalendar/kalendar.py"
try:
    subprocess.run([kalendar_script, zeitraum], check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Fehler beim Aufruf von kalendar.py: {e}")
