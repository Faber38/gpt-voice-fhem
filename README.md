
# 📢 Sprachsteuerung für FHEM – Lokal & Offline

Willkommen zu meinem **lokalen Sprachsystem** für die Haussteuerung mit **Wakeword-Erkennung, Sprachtranskription, GPT-Analyse und FHEM-Anbindung** – komplett **offline** und optimiert für **schnelle Reaktionen**!

---

## 🔥 Features

- **Wakeword-Erkennung:**  
  - Echtzeit-Erkennung über Vosk (`alexa`)
- **Sprachtranskription:**  
  - Schnell & präzise mit Faster-Whisper (`small` Modell, GPU-optimiert)
- **Sprachbefehlsverarbeitung:**  
  - Temperaturabfragen
  - Timer setzen
  - Plaudermodus ("rede mit mir")
  - Hausautomation (z.B. Licht, Rolläden) über FHEM
- **Text-to-Speech (TTS):**  
  - Klare deutsche Sprachausgabe mit Coqui TTS (Thorsten)
- **Audio-Ausgabe:**  
  - Zuverlässige Audiowiedergabe (mit Retry bei Gerätblockaden)
- **Vollständig lokal:**  
  - Keine Cloud-Dienste, keine Internetverbindung nötig
- **GPU-Unterstützung:**  
  - CUDA-Beschleunigung für Whisper und GPT

---

## ⚙️ Architektur

```text
Wakeword → Sprachaufnahme → Transkription (Whisper) → 
Textfilter → Befehlserkennung → 
Aktion (z.B. Timer, Temperatur, FHEM) → 
Antwort per TTS
```

---

## 🛠️ Komponenten

| Komponente          | Beschreibung |
|:--------------------|:--------------|
| `wakeword_niko.py`   | Hauptprozess: Lauschen, Aufnahme, Befehlsauswertung |
| `gpt_temp.py`        | Temperaturabfrage und freundliche Antwort über GPT |
| `timer.py`           | Timer setzen und ablaufen lassen |
| `kalendar.py`        | *ics Datei abfragen! |
| `gpt_to_fhem.py`     | Sprachsteuerung an FHEM senden |
| `filter.py`          | Texte filtern und vereinfachen |
| `/opt/sound/`        | WAV-Dateien für Antworten, Timer, Fehler |

---

## 🧰 Abhängigkeiten

- **Python 3.11**
- `vosk`, `sounddevice`, `samplerate`
- `numpy`, `librosa`, `faster-whisper`
- `TTS (coqui-ai)`, `llama-cpp-python`
- optional: CUDA für GPU-Beschleunigung

Installation über venv (empfohlen):

```bash
python3 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt
```

---

## 🏁 Starten

1. Wakeword-System starten:

```bash
/opt/script/start_voice_system.sh
```

(Dient als Service: `voice_system.service`)

2. Sprachbefehl aussprechen → System reagiert automatisch.

---

## 📦 Verzeichnisstruktur

```text
/opt/
 ├── script/
 │    ├── wakeword_niko.py
 │    ├── gpt_temp.py
 │    ├── timer.py
 │    ├── gpt_to_fhem.py
 │    └── filter.py
 ├── sound/
 │    ├── responses/
 │    ├── confirm/
 │    ├── error/
 │    ├── timer/
 ├── venv/
 ├── vosk/
 ├── mistral-7b-instruct-v0.1.Q4_K_M.gguf
```

---

## 🧹 To-Do

- [x] Wakeword-Erkennung stabilisieren
- [x] Temperatur & Timer-Logik sauber trennen
- [ ] Mehrere parallele Timer ermöglichen
- [ ] Web-Interface für Timer-Status
- [ ] Bessere Fehlerbehandlung bei Audio

---

## 🧑‍💻 Autor

Projekt von **Faber38**  
→ für privates Haussteuerungssystem auf **Debian VM (Proxmox)** mit **lokalem Sprachmodell**.

---

# 🚀 Viel Spaß beim Nachbauen und Weiterentwickeln!
