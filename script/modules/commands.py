import subprocess
import os
import glob
import random
import difflib
import threading
import time

stream = None  # Wird per set_stream() gesetzt
ENABLE_FRAGE_MODUL = False  # ⛘ aktuell deaktiviert

def set_stream(extern_stream):
    global stream
    stream = extern_stream

def pausiere_mikrofon():
    try:
        if stream and stream.active:
            stream.stop()
            print("🔇 Mikrofon pausiert")
    except Exception as e:
        print(f"⚠️ Fehler beim Pausieren des Mikrofons: {e}")

def aktiviere_mikrofon():
    try:
        if stream and not stream.active:
            stream.start()
            print("🎤 Mikrofon wieder aktiviert")
    except Exception as e:
        print(f"⚠️ Fehler beim Aktivieren des Mikrofons: {e}")

def mikrofon_reaktivieren_nach_delay(delay=6):
    def reaktivieren():
        aktiviere_mikrofon()
    threading.Timer(delay, reaktivieren).start()

def mikrofon_neustart(delay=0.3):
    global stream
    try:
        if stream:
            print("🔁 Erzwinge vollständigen Mikrofon-Neustart …")
            stream.stop()
            stream.close()
            time.sleep(delay)
            stream.start()
            print(f"✅ Mikrofon erfolgreich neu gestartet – aktiv: {stream.active}")
    except Exception as e:
        print(f"❌ Fehler beim Mikrofon-Neustart: {e}")

def _play_wav_from_folder(folder, filename=None, retries=3, delay=0.3):
    if filename:
        wav_path = os.path.join(folder, filename)
    else:
        files = glob.glob(os.path.join(folder, "*.wav"))
        if not files:
            print(f"⚠️ Keine WAV-Dateien im Ordner {folder} gefunden.")
            return
        wav_path = random.choice(files)
        filename = os.path.basename(wav_path)

    try:
        with open("/opt/script/audio_device.conf", "r") as f:
            alsa_dev = f.read().strip()
    except Exception as e:
        print(f"❌ Fehler beim Lesen von audio_device.conf: {e}")
        return

    for attempt in range(retries):
        try:
            open("/tmp/mic_paused", "w").close()
            subprocess.run(["aplay", "-D", alsa_dev, wav_path], check=True)
            if os.path.exists("/tmp/mic_paused"):
                os.remove("/tmp/mic_paused")
            print(f"▶️ WAV abgespielt: {filename}")
            return
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Versuch {attempt+1}/{retries} fehlgeschlagen: {e}")
            time.sleep(delay)

    print(f"❌ Konnte Datei nicht abspielen: {filename}")
    if os.path.exists("/tmp/mic_paused"):
        os.remove("/tmp/mic_paused")

def play_response_wav(filename=None):
    _play_wav_from_folder("/opt/sound/responses", filename)

def play_error_wav(filename=None):
    _play_wav_from_folder("/opt/sound/error", filename)

def play_confirm_wav(filename=None):
    _play_wav_from_folder("/opt/sound/confirm", filename)

def play_wetter_wav(filename=None):
    _play_wav_from_folder("/opt/sound/wetter", filename)

def play_temp_wav(filename=None):
    _play_wav_from_folder("/opt/sound/temperatur", filename)
        
def handle_kalender(filtered_text):
    if "kalender" not in filtered_text.lower():
        return False

    print("🗖️ Kalenderbefehl erkannt")
    pausiere_mikrofon()
    play_confirm_wav()  # ⌚ zufällige freundliche Ansage

    if "morgen" in filtered_text.lower():
        arg = "morgen"
    elif "heute" in filtered_text.lower():
        arg = "heute"
    elif "woche" in filtered_text.lower() or "diese woche" in filtered_text.lower():
        arg = "woche"
    else:
        arg = "woche"

    print(f"➡️ Zeige Kalender: {arg}")
    os.system(f"/opt/venv/bin/python3 /opt/script/kalendar.py {arg}")

    mikrofon_reaktivieren_nach_delay()
    return True
  

def lade_erlaubte_orte(pfad="/opt/script/orte.txt"):
    try:
        with open(pfad, "r") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Fehler beim Laden der Ortsliste: {e}")
        return []


def finde_bestpassenden_ort(erkannt, erlaubte_orte):
    treffer = difflib.get_close_matches(erkannt.lower(), erlaubte_orte, n=1, cutoff=0.6)
    if treffer:
        print(f"🧠 Ort '{erkannt}' korrigiert zu '{treffer[0]}'")
        return treffer[0]
    return None


def handle_wetter(filtered_text):
    if "wetter" not in filtered_text.lower():
        return False

    print(f"🌦️ Wetterbefehl erkannt: {filtered_text}")
    orte_liste = lade_erlaubte_orte()
    worte = filtered_text.lower().split()

    zeitpunkt = "heute"
    for z in ("morgen", "heute"):
        if z in worte:
            zeitpunkt = z
            break

    kandidaten = [w for w in reversed(worte) if w not in ("wetter", "morgen", "heute", "wie", "wird", "das", "in")]
    ort_roh = kandidaten[0] if kandidaten else None
    ort_final = finde_bestpassenden_ort(ort_roh, orte_liste) if ort_roh else None

    if not ort_final:
        print("⚠️ Kein gültiger Ort erkannt – wetter.py wird nicht gestartet.")
        return False

    pausiere_mikrofon()
    play_wetter_wav()  # ⛅ freundliche Wetter-Antwort vorab
    cmd = ["/opt/venv/bin/python", "/opt/script/wetter.py", "wetter", zeitpunkt, ort_final]
    print(f"🧪 Starte wetter.py: {' '.join(cmd)}")
    subprocess.run(cmd)
    aktiviere_mikrofon()
    return True


def handle_temperature(filtered_text):
    if "temperatur" not in filtered_text.lower():
        return False

    print(f"🌡️ Temperaturabfrage erkannt: {filtered_text}")
    pausiere_mikrofon()
    play_temp_wav()  # ❄️ freundliche Reaktion vor Temperaturabfrage
    try:
        result = subprocess.run(
            ["/opt/venv/bin/python", "/opt/script/gpt_temp.py", "--text", filtered_text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=25
        )
        for line in result.stdout.splitlines():
            print(f"[gpt_temp] {line.strip()}")
        for line in result.stderr.splitlines():
            print(f"[gpt_temp ERROR] {line.strip()}")
        print(f"✅ gpt_temp.py abgeschlossen (Exitcode {result.returncode})")
        return True
    except subprocess.TimeoutExpired:
        print("❌ gpt_temp.py hängt – Timeout erreicht!")
    except Exception as e:
        print(f"❌ Fehler beim Start von gpt_temp.py: {e}")
    finally:
        try:
            # Expliziter Mikrofon-Neustart nach Temperatur
            from modules.commands import aktiviere_mikrofon
            time.sleep(0.3)
            aktiviere_mikrofon()
            print("🎤 Mikrofon vollständig neu gestartet nach Temperaturabfrage.")
        except Exception as e:
            print(f"⚠️ Fehler beim Mikrofon-Neustart nach Temperatur: {e}")
    return False


def handle_frage(filtered_text):
    if not ENABLE_FRAGE_MODUL:
        print("⛔ Frage-Modul ist deaktiviert – kein Aufruf von frage.py")
        return False

    if not filtered_text.lower().startswith("frage"):
        return False

    print(f"🧠 Wissensfrage erkannt: {filtered_text}")
    try:
        from modules.commands import pausiere_mikrofon, aktiviere_mikrofon
        pausiere_mikrofon()
        play_response_wav()  # 💡 freundliche Reaktion auf Frage
        proc = subprocess.Popen(
            ["/opt/venv/bin/python", "/opt/script/frage.py", "--text", filtered_text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Timeout-Schutz (2 Minuten)
        try:
            proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            print("⏱️ frage.py hat zu lange gebraucht – wird beendet.")
            proc.kill()

    except Exception as e:
        print(f"❌ Fehler beim Start von frage.py: {e}")
    finally:
        aktiviere_mikrofon()
    return True


def play_confirmation(output_device):
    confirm_files = glob.glob("/opt/sound/confirm/*.wav")
    if confirm_files:
        confirm_wav = random.choice(confirm_files)
        confirm_path = os.path.join("/opt/sound/confirm", confirm_wav)
        print(f"▶️ Bestätigung: {confirm_wav}")
        if output_device:
            subprocess.Popen(["aplay", "-D", output_device, confirm_path])


def play_error(output_device):
    error_files = glob.glob("/opt/sound/error/*.wav")
    if error_files:
        error_wav = random.choice(error_files)
        error_path = os.path.join("/opt/sound/error", error_wav)
        print(f"❌ Fehlerausgabe: {error_wav}")
        if output_device:
            subprocess.Popen(["aplay", "-D", output_device, error_path])

def handle_timer(filtered_text, output_device):
    import re
    match = re.match(r".*timer.*für\s+(\d+)\s+(sekunden|minuten|stunden)", filtered_text.lower())
    if not match:
        return False

    zahl = match.group(1)
    einheit = match.group(2)
    print(f"⏲️ Starte Timer für {zahl} {einheit} ...")
    try:
        play_confirm_wav()  # 🕒 Freundliche Timer-Bestätigung
        open("/tmp/mic_paused", "w").close()
        subprocess.Popen([
            "/opt/venv/bin/python", "/opt/script/timer.py", zahl, einheit
        ], start_new_session=True)
        return True
    except Exception as e:
        print(f"❌ Fehler beim Start von timer.py: {e}")
        return False
