📦 gpt-voice-fhem

A local voice control system for FHEM, based on Vosk speech recognition and Python. No cloud services involved – fully offline.

Features:

    Wakeword detection ("niko")

    16 kHz audio recording via ALSA (e.g. PowerConf S3)

    Speech recognition with Vosk

    Command filtering and FHEM execution

    Spoken responses (Coqui TTS / WAV playback)

    All services startable via systemd or manually

    Easily extendable with local GPT models (optional)
