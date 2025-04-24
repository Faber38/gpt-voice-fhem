#!/usr/bin/env python3
import sounddevice as sd

# 🔧 Konfiguriertes Device-Label aus Datei lesen
DEVICE_CONF = "/opt/script/audio_device.conf"
INDEX_CONF = "/opt/script/audio_index.conf"

try:
    with open(DEVICE_CONF, "r") as f:
        device_hint = f.read().strip()
except Exception as e:
    print(f"❌ Fehler beim Lesen der config: {e}")
    exit(1)

# 🔍 Suche passenden Index in Sounddevice
def find_device_index(hint):
    for index, dev in enumerate(sd.query_devices()):
        name = dev.get("name", "")
        if hint in name:
            return index
    return None

index = find_device_index("PowerConf S3")
if index is not None:
    print(f"✅ Gefunden: Device-Index = {index}")
    try:
        with open(INDEX_CONF, "w") as f:
            f.write(str(index))
        print(f"📁 Gespeichert in: {INDEX_CONF}")
    except Exception as e:
        print(f"❌ Fehler beim Schreiben der Index-Datei: {e}")
else:
    print("❌ Kein passendes Audio-Device gefunden.")
