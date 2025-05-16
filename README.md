
# 📢 Sprachsteuerung für FHEM – Lokal & Offline

Willkommen zu meinem **lokalen Sprachsystem** für die Haussteuerung mit **Wakeword-Erkennung, Sprachtranskription, GPT-Auswertung und FHEM-Anbindung** – komplett **offline**, **rasant schnell** und **vollständig lokal auf deinem Gerät**!

---

## 🔥 Features

- **Wakeword-Erkennung:**  
  - Reagiert auf **„alexa“** per Vosk (deutsches Offline-Modell)
- **Sprachtranskription:**  
  - Offline über Vosk – kein Whisper, keine Internetverbindung
- **Sprachbefehlsverarbeitung:**  
  - Licht & Rollos steuern (FHEM)
  - Temperaturstatus abfragen
  - Kalenderansagen (lokal)
  - Smalltalk („rede mit mir“)
- **Text-to-Speech (TTS):**  
  - Klare deutsche Sprachausgabe mit Coqui TTS (Thorsten), lokal per GPU
- **Audio-Ausgabe:**  
  - Stabile Wiedergabe via `aplay`, Gerät über `audio_device.conf` konfigurierbar
  - Zufällige Bestätigungs- und Fehlermeldungen
- **Vollständig offline:**  
  - Kein Cloudzugriff, keine Internetverbindung nötig
- **GPU-Unterstützung:**  
  - CUDA-Beschleunigung für GPT (TinyLlama, Phi, Mistral)

---

## ⚙️ Architektur

```text
Wakeword (alexa) → Aufnahme (8 Sek.) → Vosk-Transkription → 
→ GPT-Auswertung (lokal, tinyllama/phi) → 
→ Befehl an FHEM (via gpt_to_fhem.py) → 
→ Antwort per Coqui TTS → Audio-Ausgabe
```

---

## 🛠️ Komponenten

| Komponente              | Beschreibung |
|-------------------------|--------------|
| `wakeword_niko.py`      | Hauptprozess: Wakeword, Aufnahme, Weitergabe |
| `gpt_to_fhem.py`        | Extrahiert Befehl aus Text und steuert FHEM |
| `filter.py`             | Bereinigt Eingabetext (z. B. "mach das Licht im Bad an") |
| `play_random_response.py` | Spielt zufällige Bestätigungsantwort ab |
| `play_random_error.py`    | Spielt zufällige Fehlermeldung ab |
| `wetter.py`             | Wetterdaten online holen, ausgeben per TTS |
| `frage.py`              | Allgemeine Fragen lokal beantworten |
| `audio_device.conf`     | Definiert Audio-Ausgabegerät (z. B. `hw:CARD=S3,DEV=0`) |

---

## 🔉 Soundstruktur

```text
/opt/sound/
 ├── responses/    → Zufällige Antworten nach Wakeword
 ├── confirm/      → „Wird erledigt“-Antworten
 ├── error/        → Fehlermeldungen bei Nichtverstehen
 ├── timer/        → Klingelton etc.
```

---

## 🧰 Abhängigkeiten

- **Python 3.11**
- `vosk`, `sounddevice`, `numpy`, `librosa`, `samplerate`
- `TTS (coqui-ai)`, `llama-cpp-python`
- Optional: CUDA-Treiber für GPU-Beschleunigung

Installation via `venv`:

```bash
python3 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt
```

---

## 🏁 Starten

1. System starten:

```bash
/opt/script/start_voice_system.sh
```

(Der Dienst `voice_system.service` kann diesen Aufruf automatisieren.)

2. Sag z. B. **„Alexa, mach im Wohnzimmer das Licht an“** – das System erkennt, verarbeitet, antwortet – **alles lokal.**

---

## 📦 Projektstruktur

```text
/opt/
 ├── script/
 │    ├── wakeword_niko.py
 │    ├── gpt_to_fhem.py
 │    ├── filter.py
 │    ├── wetter.py
 │    ├── frage.py
 │    ├── play_random_response.py
 │    ├── play_random_error.py
 │    └── audio_device.conf
 ├── sound/
 │    ├── responses/
 │    ├── confirm/
 │    ├── error/
 │    └── timer/
 ├── venv/
 ├── vosk/
 │    └── vosk-de/
 ├── models/
 │    └── phi-2.Q4_K_M.gguf
```

---

## ✅ To-Do

- [x] Wakeword stabilisiert mit Vosk („alexa“)
- [x] GPT-Eingabe über lokale Modelle
- [x] FHEM-Steuerung funktioniert vollständig
- [x] Antwortsystem mit Coqui TTS
- [ ] Statusabfrage für CPU, RAM etc. per Sprache
- [ ] Web-Interface zur MAC-Whitelist im Hotspot

---

## 👤 Autor

Projekt von **Faber38**  
→ Lokale Sprachsteuerung für Hausautomation mit Vosk, Coqui, GPT & FHEM  
→ Läuft auf Debian VM (Proxmox) mit GPU-Beschleunigung (CUDA)

---

# 🚀 Viel Spaß beim Ausprobieren und Erweitern!
