# 🗣️ GPT-Voice-FHEM

**Lokale Sprachsteuerung für FHEM – offline, sicher und schnell.**

Dieses Projekt verwandelt ein Mikrofon in eine smarte Sprachsteuerung für dein Smart Home – ganz ohne Cloud!  
Die Erkennung erfolgt über Vosk (lokale Spracherkennung) und die Verarbeitung über TinyLlama + Coqui TTS.

### 💡 Features

- Wakeword-Erkennung ("niko") mit Vosk
- Sprachaufnahme & Transkription lokal (**faster-whisper** für Sound → Text)
- Verarbeitung per lokalem GPT-Modell (z. B. TinyLlama)
- Gerätesteuerung über FHEM (HTTP API)
- Rückmeldung per Sprachausgabe (Coqui TTS)
- Vollständig offline & lokal

<hr style="margin:20px 0;">

<h2 style="color:#884ea0; font-size: 22px; margin: 20px 0;">🧠 GPT Sprachsteuerung</h2>
<p>Lokale Sprachsteuerung über Wakeword & GPT-Anbindung zur Steuerung von FHEM.</p>

<h3 style="color:#117a65;">🔊 Details:</h3>
<ul>
  <li><strong>Wakeword:</strong> "niko"</li>
  <li><strong>Transkription:</strong> faster-whisper (CUDA-beschleunigt)</li>
  <li><strong>TTS:</strong> Coqui / lokale Sprachausgabe</li>
  <li><strong>Hardware:</strong> PowerConf S3 Lautsprecher & RØDE Wireless GO II Mikrofon, RTX 3060 (CUDA)</li>
  <li><strong>Modelle:</strong> TinyLlama, Phi-2</li>
</ul>

<h3 style="color:#b9770e;">⚙️ Verzeichnisse:</h3>
<ul>
  <li><code>/opt/script/</code> → Steuerungs-Skripte</li>
  <li><code>/opt/sound/</code> → Sprachantworten</li>
  <li><code>/opt/vosk/</code> → Sprachmodelle</li>
</ul>

<hr>
<p style="font-size:small; color:#555;">Letzte Aktualisierung: April 2025</p>

👉 Für die vollständige Einrichtung siehe [INSTALL.md](INSTALL.md)

