import os

# 🔄 Korrekturen aus Dateien laden
def lade_korrekturen(pfad="/opt/script/korrektur"):
    corrections = {}
    for dateiname in sorted(os.listdir(pfad)):
        if dateiname.endswith(".txt"):
            dateipfad = os.path.join(pfad, dateiname)
            with open(dateipfad, "r", encoding="utf-8") as f:
                for zeile in f:
                    zeile = zeile.strip()
                    if not zeile or zeile.startswith("#"):
                        continue  # Kommentare oder leere Zeilen überspringen
                    if "|" in zeile:
                        falsch, richtig = zeile.split("|", 1)
                        corrections[falsch.strip()] = richtig.strip()
    return corrections

# Gerät- und Synonym-Liste
device_dict = {
    "rollade": ["rollladen", "rollo", "rollen", "jalousie", "war laden", "lade", "war lade", "roller de", "vorlage", "rolle hatte"],
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

# Füllwörter entfernen
def remove_fuellwoerter(text):
    fuellwoerter = [
        "bitte", "mach", "mache", "kannst", "du", "das", "den", "die",
        "in", "wer", "im", "der", "lade", "nordlicht", "fahre", "ihre", "farbe",
    ]
    return " ".join([w for w in text.split() if w not in fuellwoerter])

# Zahlwörter ersetzen
def ersetze_zahlwoerter(text):
    worte = {
        "null": "0",
        "fünf": "5",
        "zehn": "10",
        "fünfzehn": "15",
        "zwanzig": "20",
        "fünfundzwanzig": "25",
        "dreißig": "30",
        "fünfunddreißig": "35",
        "vierzig": "40",
        "fünfundvierzig": "45",
        "fünfzig": "50",
        "fünfundfünfzig": "55",
        "sechzig": "60",
        "fünfundsechzig": "65",
        "siebzig": "70",
        "fünfundsiebzig": "75",
        "achtzig": "80",
        "fünfundachtzig": "85",
        "neunzig": "90",
        "fünfundneunzig": "95",
        "hundert": "100"
    }
    return " ".join([worte.get(w, w) for w in text.split()])

# Text bereinigen und normalisieren
def clean_text(user_input):
    print(f"🎧 Original: {user_input}")
    if not user_input:
        print("❌ Eingabe ist leer!")
        return ""

    # Korrekturen laden
    corrections = lade_korrekturen()

    text = user_input.lower()
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    text = normalize_device(text)
    text = remove_fuellwoerter(text)
    text = ersetze_zahlwoerter(text)

    print(f"✅ Ergebnis: {text}")
    return text
