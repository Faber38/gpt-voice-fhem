#!/opt/venv/bin/python3
import sys
import os
import re
from filter import clean_text  # Die Filterfunktion aus deinem filter.py importieren

# Gerät- und Synonym-Liste (aus device.txt)
device_dict = {
    "rollade": ["rollladen", "rollo", "rollen", "jalousie"],
    "licht": ["lampe", "beleuchtung", "lichtquelle"],
    "hilfe": ["hilft", "hilfen"],
    "bei": ["bei", "bye"],
}

# Normalisierung der Gerätebezeichner
def normalize_device(text):
    for device, synonyms in device_dict.items():
        for synonym in synonyms:
            text = text.replace(synonym, device)
    return text

# Geräte und Synonyme aus device.txt laden
def lade_device_file():
    device_file_path = "/opt/script/device.txt"
    devices = {}
    try:
        with open(device_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "|" in line:
                    parts = line.split("|")
                    device_name = parts[0].strip()
                    synonyms = [synonym.strip() for synonym in parts[1].split()]
                    devices[device_name] = synonyms
    except Exception as e:
        print(f"❌ Fehler beim Laden der device.txt: {e}")
    return devices

# Text durch den Filter und Gerätecheck laufen lassen
def process_text(user_input):
    print(f"🎧 Original Text: {user_input}")
    
    # Filter anwenden
    filtered_text = clean_text(user_input)  # Durch den Filter

    # Normalisierung und Ersetzung von Synonymen
    devices = lade_device_file()  # Lade Gerätebezeichner aus device.txt
    filtered_text = normalize_device(filtered_text)  # Normalisiere Gerätebezeichner

    print(f"📝 Gefilterter Text nach Normalisierung: {filtered_text}")
    
    return filtered_text

# Hauptlogik
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Bitte gib einen Text zum Testen an!")
        sys.exit(1)

    # Text vom Benutzer
    user_input = " ".join(sys.argv[1:])

    # Text durch den Filter und die Normalisierung schicken
    final_result = process_text(user_input)

    print(f"✅ Endgültiges Ergebnis: {final_result}")
