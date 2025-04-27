# 🗣️ GPT-Voice-FHEM

**Local voice control for FHEM – offline, secure, and fast.**

This project turns a microphone into a smart voice controller for your smart home – completely cloud-free!  
Wakeword detection is powered by Vosk, speech-to-text by faster-whisper, and processing via TinyLlama + Coqui TTS.

### 💡 Features

- Wakeword detection ("niko") using Vosk
- Local speech recording & transcription (**faster-whisper** for audio → text)
- Processing via local GPT models (e.g., TinyLlama)
- Device control via FHEM (HTTP API)
- Voice feedback using Coqui TTS
- Fully offline & local

<hr style="margin:20px 0;">

<h2 style="color:#884ea0; font-size: 22px; margin: 20px 0;">🧠 GPT Voice Control</h2>
<p>Local voice control with wakeword detection and GPT integration to control FHEM devices.</p>

<h3 style="color:#117a65;">🔊 Details:</h3>
<ul>
  <li><strong>Wakeword:</strong> "niko"</li>
  <li><strong>Transcription:</strong> faster-whisper (CUDA-accelerated)</li>
  <li><strong>TTS:</strong> Coqui / local speech synthesis</li>
  <li><strong>Hardware:</strong> PowerConf S3 speaker & RØDE Wireless GO II microphone, RTX 3060 (CUDA)</li>
  <li><strong>Models:</strong> TinyLlama, Phi-2</li>
</ul>

<h3 style="color:#b9770e;">⚙️ Directories:</h3>
<ul>
  <li><code>/opt/script/</code> → Control scripts</li>
  <li><code>/opt/sound/</code> → Voice responses</li>
  <li><code>/opt/vosk/</code> → Speech recognition models</li>
</ul>

<hr>
<p style="font-size:small; color:#555;">Last updated: April 2025</p>

👉 For full setup instructions, see [INSTALL.md](INSTALL.md)
