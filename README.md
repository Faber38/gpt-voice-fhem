# gpt-voice-fhem

Lokale Sprachsteuerung für FHEM über GPT-Modelle.

## Projektbeschreibung

Dieses Projekt ermöglicht die Sprachsteuerung von FHEM über lokal laufende GPT-Modelle.  
Es werden keine Cloud-Dienste verwendet — alles bleibt lokal auf eigener Hardware.

Getrennte Architektur:

- GPT Sprachserver (z.B. auf eigener VM)
- FHEM Server (z.B. separate VM)
- Kommunikation über HTTP API

---

## Projektstruktur

├── src/ → Python Quellcode für Sprachlogik / API ├── fhem/ → FHEM Konfiguration (z.B. DOIF, Dummy Devices) ├── docs/ → Dokumentation, Sprachbefehle usw. ├── requirements.txt → Python Abhängigkeiten └── config.yaml → Konfigurationsdatei für Server


---

## Ziel

Einfacher und lokal betriebener Sprachassistent zur Steuerung von Geräten im Smart Home (FHEM).

---

## Status

- Sprachsteuerung für Licht funktioniert
- Ausbaubar auf weitere Geräte und Räume

---

## ToDo

- Weitere Sprachbefehle
- Variablenerkennung verbessern
- Doku erweitern
- Automatisierte Tests

---

## Lizenz

Private Nutzung — Open Source — Keine Gewährleistung

