# /opt/script/filter.py

# Gerät- und Synonym-Liste
device_dict = {
    "rollade": ["rollladen", "rollo", "rollen", "jalousie", "war laden", "lade", "war lade", "roller de", "vorlage", "rolle hatte"],
    "licht": ["lampe", "beleuchtung", "lichtquelle"],
    "hilfe": ["hilft", "hilfen"],
    "bei": ["Bei", "bye"],
    # Weitere Geräte und deren Synonyme können hier hinzugefügt werden
}

# Normalisierung der Gerätebezeichner
def normalize_device(text):
    for device, synonyms in device_dict.items():
        for synonym in synonyms:
            text = text.replace(synonym, device)  # Ersetze jedes Synonym durch das korrekte Gerät
    return text

def normalize_text(text):
    if not text:
        print("❌ Der Text ist leer!")
        return text  # Wenn der Text leer ist, wird nichts weiter geändert

    corrections = {
        "ron t r": "runter",
        "ronter": "runter",
        "unter": "runter",
        "darunter": "runter",
        "darrunter": "runter",
        "rrunter": "runter",
        "hochher": "hoch",
        "man": "",
        "rolle": "rollade",  # Diese Zeile sollte nach der Behandlung von "rolrollade" kommen
        "roller": "rollade",
        "rollladen": "rollade",
        "rollo": "rollade",
        "hilfen hilfe zu rollade": "hilfe zu rollade",
        "hilft zu rollade": "hilfe zu rollade",
        "hilfe bei war rollade": "hilfe zu rollade",
        "hilfe bei rourollade": "hilfe zu rollade",
        "hilfe zu war laden": "hilfe zu rollade",
        "tageslicht an": "tageslicht an",  # Der Befehl bleibt unverändert
        "tageslicht aus": "tageslicht aus",  # Der Befehl bleibt unverändert
        "urlaubsmodus aktivieren": "urlaubsmodus aktivieren",  # Unverändert, Befehl wird durchgelassen
        "urlaub einschalten": "urlaubsmodus aktivieren",  # Umwandeln in den gleichen Befehl wie oben
        "normalmodus an": "normalmodus an",  # Unverändert, Befehl wird durchgelassen
        "zurück auf normal": "normalmodus an",  # Umwandeln in den gleichen Befehl wie oben
        "urlaubs modus": "urlaubsmodus",
        "rollade automatik": "rolladenautomatik",
        "temperatur wohnzimmer": "temperatur wohnzimmer",  # Für Temperaturabfrage
    }

    # Verhindern, dass "rolrollade" fälschlicherweise in "rollade" umgewandelt wird
    if "rolrollade" in text:
        text = text.replace("rolrollade", "rollade")
    if "rolrollade" in text:
        text = text.replace("rourollade", "rollade")
    if "rolrollade" in text:
            text = text.replace("roll rollade", "rollade")


    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    return text.strip()

# Füllwörter entfernen
def remove_fuellwoerter(text):
    fuellwoerter = [
        "bitte", "mach", "mache", "kannst", "du", "das", "den", "die",
        "in", "wer", "im", "der", "lade", "nordlicht", "fahre", "ihre", "farbe",
    ]
    return " ".join([w for w in text.split() if w not in fuellwoerter])

# Rollade automatisch ergänzen
def auto_ergaenze_rollade(text):
    bewegung_woerter = ["raus", "rein", "runter", "unter", "rauf", "hoch", "auf"]
    rollo_begriffe = ["rollade"]
    if not any(w in text for w in rollo_begriffe):
        for wort in bewegung_woerter:
            if wort in text.split():
                print("🧠 Ergänze fehlendes Gerät: Rollade")
                return text.replace(wort, f"rollade {wort}")
    return text

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
    
    # Stellen Sie sicher, dass die Eingabe nicht leer ist, bevor sie an die Funktion weitergegeben wird
    if not user_input:
        print("❌ Eingabe ist leer!")
        return ""

    text = normalize_device(user_input)  # Zuerst die Gerätebezeichner normalisieren
    text = remove_fuellwoerter(text)  # Füllwörter entfernen
    text = normalize_text(text)  # Zuerst die bekannten Fehler und Synonyme normalisieren
    print(f"🧹 Gefiltert: {text}")
   # text = auto_ergaenze_rollade(text)  # Rolladen-Devices automatisch ergänzen
    text = ersetze_zahlwoerter(text)  # Zahlwörter umwandeln
    print(f"✅ Ergebnis: {text}")
    return text
