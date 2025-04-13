
# gpt-voice-fhem

## Projektbeschreibung

Dieses Projekt ermöglicht eine lokale Sprachsteuerung von FHEM über GPT-Modelle.

Sprachbefehle werden per HTTP an den Sprachserver gesendet und in FHEM über DOIF-Logik verarbeitet.

Die Sprachlogik in FHEM wird über DOIF und Dummy-Devices in der Datei `fhem/gpt.cfg` umgesetzt.

Beispiel:
- Sprachbefehl:  
  `"Schalte das Licht in der Küche an"`
- Ergebnis:  
  DOIF in FHEM schaltet das Küchenlicht über Homematic Aktor.

## Projektstruktur

```
├── src/                → Python Quellcode für Sprachlogik / API (Flask)
├── fhem/               → FHEM Konfiguration (z.B. DOIF, Dummy Devices in gpt.cfg)
├── docs/               → Dokumentation, Sprachbefehle, Beispiele
├── requirements.txt    → Python Abhängigkeiten
├── config.yaml         → Konfigurationsdatei für GPT Server (IP, API-Key, Port)
└── README.md           → Projektbeschreibung
```

## Voraussetzungen

- FHEM installiert (getestet auf Debian)
- Python 3.x Umgebung
- Lokaler Sprachserver (getestet mit GPT4All / MPT / ollama)
- Modelle: Sprachmodelle lokal (kein Cloud-Zugriff nötig)

## Installation (Kurzform)

Auf dem GPT-Sprachserver:

```bash
git clone git@github.com:Faber38/gpt-voice-fhem.git
cd gpt-voice
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/server.py
```

## Beispiel Sprachbefehl per curl

```bash
curl -X POST http://<Sprachserver-IP>:5000/api/voicecmd -H "Content-Type: application/json" -d '{"text": "Schalte das Licht in der Küche an"}'
```

## FHEM Integration

Die Datei `fhem/gpt.cfg` enthält alle GPT-Logiken:

- Dummy `GptVoiceCommand`
- DOIF `di_gpt_Kuechenlicht`
- Weitere Geräte werden hier ergänzt

## ToDo

- Weitere Sprachbefehle / Geräte ergänzen
- Beispiel-Skripte zur Einrichtung Sprachserver
- Dokumentation weiter ausbauen

---

## Lizenz / Nutzung

Dieses Projekt dient als private Sprachsteuerung für FHEM SmartHome Systeme.  
Verwendung und Anpassung auf eigene Verantwortung.  

(c) 2025 Faber38  


Stand: April 2025  
Autor: github.com/Faber38
