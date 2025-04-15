
# Projekt Gedächtnisstütze – GPT-Voice / Whisper / FHEM

## Projektziel
Lokale Sprachsteuerung auf einem Proxmox Server:  
- Sprachbefehl per Mikrofon → Whisper (Spracherkennung) → GPT-Voice API → FHEM Steuerung

## Server / VM Setup
- Debian 12 Minimal
- Proxmox VM (IP: 192.168.38.201)
- Benutzer: gptuser

## Komponenten
| Komponente     | Funktion                 | Pfad                          |
|----------------|--------------------------|--------------------------------|
| whisper.cpp    | Lokale Spracherkennung   | /opt/whisper.cpp/              |
| rudi-voice     | Wakeword + Recording     | /home/gptuser/rudi-voice/     |
| gpt-voice      | API / Verarbeitung       | /home/gptuser/gpt-voice-fhem/ |

## Dienste
```bash
systemctl start rudi-voice.service
systemctl start whisper.service
systemctl start gptvoice.service
```

## Git / Backup
```bash
alias gptgit='/home/gptuser/git_backup_restore.sh'
```
Automatisiertes Backup und Restore nach GitHub.

## Projektstruktur GitHub
```
├── fhem/                  → FHEM Konfiguration
├── opt_whisper_cpp/       → whisper.cpp Backup
├── docs/                  → Dokumentation
├── gptmenu.sh             → Steuerungsmenü
├── git_backup_restore.sh  → Backup & Restore Script
└── README.md              → Projektbeschreibung
```

## Sprachfeedback
Töne / Sounds nach Status:
| Ereignis       | Ton         |
|----------------|-------------|
| Wakeword OK    | beep_ready.wav |
| Befehl OK      | beep_okay.wav  |
| Fehler / Unknown | beep_error.wav |

## ToDo / Zukunft
- RTX 3060 GPU → Passthrough für Whisper & GPT Optimierung
- Mehr Sprachbefehle
- Weitere Soundfiles für Rückmeldung
- Optional: Mehrsprachigkeit / Wakeword Training

---

Stand: April 2025  
Autor: github.com/Faber38  
Projekt: GPT-Voice / Whisper / FHEM SmartHome
