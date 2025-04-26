import subprocess
import time
import sys

# 📁 Pfad zur Sounddatei
wav_file = "/opt/sound/hilfe/dein_teimer_ist_abgelaufen.wav"

# 🔧 ALSA-Device aus der Konfigurationsdatei laden
with open("/opt/script/audio_device.conf", "r") as f:
    alsa_dev = f.read().strip()

# 🔔 Timer-Logik (5 Sekunden als Beispiel)
if len(sys.argv) < 3:
    print("❌ Bitte gib die Timer-Dauer und die Zeiteinheit an.")
    sys.exit(1)

# Die Zeit und Einheit vom Argument
timer_duration = int(sys.argv[1])
time_unit = sys.argv[2].lower()

# 📢 Bestätigungstext
confirmation_text = f"Timer erstellt für {timer_duration} {time_unit}."

# 🎶 Timer starten
if time_unit == "minuten":
    # Minuten-WAV und dann die Sekunden-WAV abspielen
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/teimer_erstell_fuehr.wav"])  # Text: "Timer erstellt für X Minuten"
    subprocess.run(["aplay", "-D", alsa_dev, f"/opt/sound/timer/{timer_duration}.wav"])  # z.B. "5.wav"
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/minuten.wav"])  # Minuten-Datei
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/ab_jetzt.wav"])
elif time_unit == "sekunden":
    # Sekunden-WAV und dann die Zahl als WAV abspielen
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/teimer_erstell_fuehr.wav"])  # Text: "Timer erstellt für X Sekunden"
    subprocess.run(["aplay", "-D", alsa_dev, f"/opt/sound/timer/{timer_duration}.wav"])  # z.B. "5.wav"
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/sekunden.wav"])  # Sekunden-WAV
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/ab_jetzt.wav"])
elif time_unit == "stunden":
    # Stunden-WAV und dann die Zahl als WAV abspielen
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/teimer_erstell_fuehr.wav"])  # Text: "Timer erstellt für X Stunden"
    subprocess.run(["aplay", "-D", alsa_dev, f"/opt/sound/timer/{timer_duration}.wav"])  # z.B. "1.wav"
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/stunden.wav"])  # Stunden-WAV
    subprocess.run(["aplay", "-D", alsa_dev, "/opt/sound/timer/ab_jetzt.wav"])
else:
    print(f"❌ Unbekannte Zeiteinheit: {time_unit}. Bitte 'sekunden', 'minuten' oder 'stunden' verwenden.")
    sys.exit(1)

# Timer läuft
print(f"✅ Timer für {timer_duration} {time_unit} gesetzt.")
# ⏳ Zeit in Sekunden berechnen:
if time_unit == "minuten":
    sleep_time = timer_duration * 60
elif time_unit == "stunden":
    sleep_time = timer_duration * 3600
elif time_unit == "sekunden":
    sleep_time = timer_duration
else:
    print(f"❌ Unbekannte Zeiteinheit: {time_unit}. Bitte 'sekunden', 'minuten' oder 'stunden' verwenden.")
    sys.exit(1)

# 💤 Timer schlafen lassen
print(f"⏲️ Timer läuft für {sleep_time} Sekunden...")
time.sleep(sleep_time)

# 🗣️ Ansage der ursprünglichen Zeit
try:
    subprocess.run(["aplay", "-D", alsa_dev, f"/opt/sound/timer/{timer_duration}.wav"])
    subprocess.run(["aplay", "-D", alsa_dev, f"/opt/sound/timer/{time_unit}.wav"])
except Exception as e:
    print(f"❌ Fehler beim Abspielen der Zeitansage: {e}")
# Nach dem Timer-Ablauf:
print("🔔 Timer abgelaufen!")
subprocess.run(["aplay", "-D", alsa_dev, wav_file])  # "dein_timer_ist_abgelaufen.wav"
time.sleep(1)  # Kurze Pause
subprocess.run(["aplay", "-D", alsa_dev, wav_file])  # "dein_timer_ist_abgelaufen.wav"

