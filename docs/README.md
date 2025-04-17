# gpt-voice-fhem

## Projektbeschreibung

Lokale Sprachsteuerung von FHEM über GPT-Modelle und Whisper-Spracherkennung auf einem dedizierten Server (Debian VM unter Proxmox).

- Sprachaufnahme per Wakeword ("Niko") → Whisper.cpp Speech-to-Text
- Verarbeitung via GPT (Ollama)
- Steuerung von SmartHome (FHEM) über HTTP API
- Vollständig offline, ohne Cloud-Zugriff

---

## Projektstruktur

├── src/ → Python Quellcode API (Flask GPT Voice API) ├── fhem/ → FHEM Konfiguration / Logik (DOIF, Dummy Devices) ├── rudi-voice/ → Wakeword Erkennung & Aufnahme (Vosk / sounddevice) │ ├── models/ → Vosk Sprachmodelle (Deutsch) │ ├── sounds/ → Beep Sounds & Feedback WAVs │ └── logs/ → Logfiles Wakeword & Spracherkennung ├── opt_whisper_cpp/ → Whisper.cpp Backup aus /opt/whisper.cpp ├── docs/ → Projekt-Dokumentation & Planung ├── requirements.txt → Python Abhängigkeiten ├── config.yaml → GPT API Server Konfiguration └── README.md → Dieses Dokument


---

## Technische Details

### VM Konfiguration (Proxmox)

| Ressource     | Wert                          |
|---------------|--------------------------------|
| CPU           | 1 Socket / 12 Kerne (host)    |
| RAM           | 16 GB                        |
| Storage       | SSD / VirtIO SCSI            |
| Netzwerk      | VirtIO / Bridge vmbr0        |
| IP-Adresse    | 192.168.xx.xxx               |

---

### Dienste / Services

| Dienst         | Beschreibung                            | Start über systemd               |
|----------------|-----------------------------------------|---------------------------------|
| whisper.service | Whisper.cpp Speech-To-Text Server      | TCP Port 5001                   |
| gptvoice.service| GPT Voice API / Flask Server           | TCP Port 5000                   |
| rudi-voice.service| Wakeword Listener "Niko" + Aufnahme  | Lokale Spracherkennung / Trigger|

---

## Installation

```bash
git clone git@github.com:Faber38/gpt-voice-fhem.git
cd gpt-voice-fhem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Sprachbefehl senden (Beispiel)

curl -X POST http://192.168.xx.xxx:5000/api/voicecmd \
-H "Content-Type: application/json" \
-d '{"text": "Schalte das Licht in der Küche an"}'

Nutzung Wakeword / Sprachaufnahme

    Wakeword "Niko" → bereit.wav (Signalton)

    Aufnahme 10 Sekunden → Whisper

    Ergebnis → GPT Verarbeitung

    Antwort an FHEM

    Beep-Töne je nach Status:

        okay.wav → erfolgreich

        error.wav → Fehler / Gerät nicht gefunden

ToDo / Geplant

    Erweiterung Sprachbefehle

    Logging optimieren

    Deployment Anleitung

    GPU Beschleunigung vorbereiten (RTX 3060 passthrough Proxmox)

    TTS ersetzen durch WAV Feedback

Hinweise

    Whisper.cpp läuft in /opt/whisper.cpp

    GPT Modelle liegen lokal in /opt/ollama

    Alle Services laufen automatisch nach Boot

Lizenz / Nutzung

Dieses Projekt dient ausschließlich privaten Zwecken im FHEM SmartHome Umfeld.

Verwendung und Anpassung auf eigene Gefahr.

(c) 2025 github.com/Faber38
Stand: April 2025
