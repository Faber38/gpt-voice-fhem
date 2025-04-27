# 📂 Was ist was?

Hier findest du eine Übersicht, wofür die einzelnen Dateien und Skripte in diesem Projekt gedacht sind.

---

| Datei                          | Beschreibung                                                                                 |
|--------------------------------|----------------------------------------------------------------------------------------------|
| **audio_device.conf**          | Konfiguration des Audio-Ausgabegeräts (ALSA-Gerätename z. B. `hw:CARD=S3,DEV=0`).            |
| **audio_index.conf**           | Sounddevice-Index für Wiedergabe (für `sounddevice` Library, z. B. `4`).                     |
| **audio_input.conf**           | Eingabegerät für Mikrofon (z. B. `hw:0,0`).                                                  |
| **coqui_tts.py**               | Text-to-Speech mit Coqui TTS – generiert Sprachausgabe lokal.                                |
| **device.txt**                 | Liste der steuerbaren Geräte + Aktionen (für GPT zur Befehlsvalidierung zu FHEM).            |
| **fhem_auth.conf**             | ⚠️ **Nicht enthalten** – enthält sensible HTTP-Zugangsdaten zu FHEM. <br> Diese Datei muss selbst erstellt werden. <br> **Beispiel-Inhalt:**<br> `[FHEM]` <br> `url = http://192.168.x.x:8083` <br> `user = deinBenutzername` <br> `pass = deinPasswort` |
| **filter.py**                  | Filtert erkannte Sprachtexte (z. B. um Fehler oder unerwünschte Wörter zu bereinigen). <br> Nutzt das Verzeichnis `korrektur/` mit allen `a-z.txt` als Filterregeln. |
| **gpt_to_fhem.py**             | Überträgt erkannte Sprachbefehle an FHEM (nach Verarbeitung mit GPT).                        |
| **mache_confirm.py**           | Erstellt Bestätigungs-Sounddateien (z. B. „Wird erledigt“).                                  |
| **mache_error.py**             | Erstellt Fehler-Sounddateien (z. B. „Das hat nicht funktioniert“).                           |
| **mache_hilfe.py**             | Erstellt Hilfe-Sounddateien aus einer `.txt` Datei.                                          |
| **mache_wav_vits.py**          | Erstellt Begrüßungs-Sounddateien (z. B. „Ja, bitte!“).                                       |
| **mic_gain.conf**              | Wav-Ausgabe-Verstärkung. Damit Whisper besser verstehen kann. (Nicht zu stark erhöhen!)      |
| **play_random_confirm.py**     | Spielt zufällig eine Bestätigungs-WAV ab.                                                    |
| **play_random_error.py**       | Spielt zufällig eine Fehler-WAV ab.                                                          |
| **play_random_response.py**    | Spielt zufällig eine Antwort-WAV nach Wakeword ab.                                           |
| **start_voice_system.sh**      | Startet das komplette Sprachsystem (Wakeword, TTS, FHEM-Anbindung etc.).                     |
| **test.py**                    | Allgemeines Test-Script für Filter-Funktionen. Beispiel: <br> `/opt/venv/bin/python3 /opt/script/test.py "fahre die markisen hinein"` |
| **timer.py**                   | Timer-Script für z. B. "Erstelle einen Wecker für 5 Sekunden". <br> Verzeichnis `/sound/timer/` erforderlich. |
| **unrecognized.log**           | Log-Datei für nicht erkannte Sprachbefehle.                                                  |
| **wakeword_niko.py**           | Haupt-Skript für Wakeword-Erkennung und Sprachaufnahme.                                      |

---

