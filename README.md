# 🗣️ GPT-Voice-FHEM

**Lokale Sprachsteuerung für FHEM – offline, sicher und schnell.**

Dieses Projekt verwandelt ein Mikrofon in eine smarte Sprachsteuerung für dein Smart Home – ganz ohne Cloud!  
Die Erkennung erfolgt über Vosk (lokale Spracherkennung) und die Verarbeitung über TinyLlama + Coqui TTS.

### 💡 Features

- Wakeword-Erkennung ("niko") mit Vosk
- Sprachaufnahme & Transkription lokal (Vosk)
- Verarbeitung per lokalem GPT-Modell (z. B. TinyLlama)
- Gerätesteuerung über FHEM (HTTP API)
- Rückmeldung per Sprachausgabe (Coqui TTS)
- Vollständig offline & lokal

👉 Für die vollständige Einrichtung siehe [INSTALL.md](INSTALL.md)
