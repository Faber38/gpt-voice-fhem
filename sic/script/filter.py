import os
import re  # ⬅️ oben sicherstellen!

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
    "rollade": ["rollo", "jalousie", "vorlage"],
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
        "bitte", "man", "mach", "mache", "kannst", "du", "das", "den", "die",
        "in", "wer", "im", "der", "lade", "nordlicht", "fahre", "ihre", "farbe",
    ]
    return " ".join([w for w in text.split() if w not in fuellwoerter])

# Zahlwörter ersetzen
def ersetze_zahlwoerter(text):
    worte = {
        "eins": "1", 
        "zwei": "2",
        "drei": "3",
        "vier": "4",
        "fünf": "5",
        "sechs": "6",
        "sieben": "7",
        "acht": "8",
        "neun": "9",
        "zehn": "10",
        "elf": "11",
        "zwölf": "12",
        "dreizehn": "13",
        "vierzehn": "14",
        "fünfzehn": "15",
        "sechzehn": "16",
        "siebzehn": "17",
        "achtzehn": "18",
        "neunzehn": "19",
        "zwanzig": "20",
        "einundzwanzig": "21",
        "zweiundzwanzig": "22",
        "dreiundzwanzig": "23",
        "vierundzwanzig": "24",
        "fünfundzwanzig": "25",
        "sechsundzwanzig": "26",
        "siebenundzwanzig": "27",
        "achtundzwanzig": "28",
        "neunundzwanzig": "29",
        "dreißig": "30",
        "einunddreißig": "31",
        "zweiunddreißig": "32",
        "dreiunddreißig": "33",
        "vierunddreißig": "34",
        "fünfunddreißig": "35",
        "sechsunddreißig": "36",
        "siebenunddreißig": "37",
        "achtunddreißig": "38",
        "neununddreißig": "39",
        "vierzig": "40",
        "einundvierzig": "41",
        "zweiundvierzig": "42",
        "dreiundvierzig": "43",
        "vierundvierzig": "44",
        "fünfundvierzig": "45",
        "sechsundvierzig": "46",
        "siebenundvierzig": "47",
        "achtundvierzig": "48",
        "neunundvierzig": "49",
        "fünfzig": "50",
        "einundfünfzig": "51",
        "zweiundfünfzig": "52",
        "dreiundfünfzig": "53",
        "vierundfünfzig": "54",
        "fünfundfünfzig": "55",
        "sechsundfünfzig": "56",
        "siebenundfünfzig": "57",
        "achtundfünfzig": "58",
        "neunundfünfzig": "59",
        "sechzig": "60",
        # Ab hier 5er Schritte
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

    corrections = lade_korrekturen()

    text = user_input.lower()

    # Alles außer Buchstaben, Zahlen, Leerzeichen → ersetzen
    text = re.sub(r'[^a-zA-Z0-9äöüÄÖÜß\s]', ' ', text)
    

    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    text = normalize_device(text)
    text = remove_fuellwoerter(text)
    text = ersetze_zahlwoerter(text)

    # 🔄 Automatische Umstellung…
    match = re.search(r"(?:timer)?\s*(?:für)?\s*(\d+)\s+(sekunden|minuten|stunden)", text)
    
    if match:
        zahl = match.group(1)
        einheit = match.group(2)
        text = f"erstelle einen timer für {zahl} {einheit}"
        print(f"🔄 Umgestellt: {text}")
    # Punkt & Satzzeichen am Ende entfernen
        text = text.strip().rstrip(".!?,")

    print(f"✅ Ergebnis: {text}")
    return text

    
