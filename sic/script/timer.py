#!/usr/bin/env python3
import subprocess
import time
import sys
import os

# 📁 Pfad zur abschließenden Sounddatei
final_wav = "/opt/sound/hilfe/dein_teimer_ist_abgelaufen.wav"

# 🔧 ALSA-Device aus Konfig laden
with open("/opt/script/audio_device.conf", "r") as f:
    alsa_dev = f.read().strip()

# 🧠 Hilfsfunktion mit Mikro-Pause
def safe_aplay_with_pause(wav_path, device, retries=5, delay=0.4):
    for attempt in range(retries):
        try:
            # ⏸️ Mikrofon pausieren
            open("/tmp/mic_paused", "w").close()
            subprocess.run(["aplay", "-D", device, wav_path], check=True)
            
            # ✅ Nur löschen, wenn vorhanden
            if os.path.exists("/tmp/mic_paused"):
                os.remove("/tmp/mic_paused")
            return
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Versuch {attempt+1}/{retries} fehlgeschlagen: {e}")
            time.sleep(delay)

    print(f"❌ Konnte {wav_path} nicht abspielen – Gerät dauerhaft belegt.")
    # 🔁 Letzter Versuch: Mikrofon-Freigabe sicherstellen
    if os.path.exists("/tmp/mic_paused"):
        os.remove("/tmp/mic_paused")


# ✅ Eingabe prüfen
if len(sys.argv) < 3:
    print("❌ Bitte gib die Timer-Dauer und die Zeiteinheit an.")
    sys.exit(1)

# ⏲️ Argumente: Dauer und Einheit
timer_duration = int(sys.argv[1])
time_unit = sys.argv[2].lower()

# 🧠 Timeransage
print(f"⏲️ Timer wird gesetzt für {timer_duration} {time_unit} ...")

# 🔉 Sprachansage zum Start
safe_aplay_with_pause("/opt/sound/timer/teimer_erstell_fuehr.wav", alsa_dev)
safe_aplay_with_pause(f"/opt/sound/timer/{timer_duration}.wav", alsa_dev)

if time_unit == "sekunden":
    safe_aplay_with_pause("/opt/sound/timer/sekunden.wav", alsa_dev)
elif time_unit == "minuten":
    safe_aplay_with_pause("/opt/sound/timer/minuten.wav", alsa_dev)
elif time_unit == "stunden":
    safe_aplay_with_pause("/opt/sound/timer/stunden.wav", alsa_dev)
else:
    print(f"❌ Unbekannte Zeiteinheit: {time_unit}")
    sys.exit(1)

safe_aplay_with_pause("/opt/sound/timer/ab_jetzt.wav", alsa_dev)

# 💤 Timer laufen lassen
if time_unit == "sekunden":
    sleep_time = timer_duration
elif time_unit == "minuten":
    sleep_time = timer_duration * 60
elif time_unit == "stunden":
    sleep_time = timer_duration * 3600
else:
    sleep_time = 0

print(f"🕒 Warte {sleep_time} Sekunden ...")
time.sleep(sleep_time)

# 🔔 Timer abgelaufen – Ansage
safe_aplay_with_pause(f"/opt/sound/timer/{timer_duration}.wav", alsa_dev)
safe_aplay_with_pause(f"/opt/sound/timer/{time_unit}.wav", alsa_dev)

print("🔔 Timer abgelaufen!")
safe_aplay_with_pause(final_wav, alsa_dev)
time.sleep(1)
safe_aplay_with_pause(final_wav, alsa_dev)
