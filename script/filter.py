# /opt/script/filter.py

def normalize_text(text):
    corrections = {
        "ron t r": "runter",
        "ronter": "runter",
        "unter": "runter",
        "darunter": "runter",
        "darrunter": "runter",
        "rrunter": "runter",
        "hochher": "hoch",
        "man": "",
        "rolle": "rollade",
        "roller": "rollade",
        "rollladen": "rollade",
        "rollo": "rollade",
        "tageslicht an": "tageslicht an",  # Der Befehl bleibt unverändert
        "tageslicht aus": "tageslicht aus",  # Der Befehl bleibt unverändert
        "urlaubsmodus aktivieren": "urlaubsmodus aktivieren",  # Unverändert, Befehl wird durchgelassen
        "urlaub einschalten": "urlaubsmodus aktivieren",  # Umwandeln in den gleichen Befehl wie oben
        "normalmodus an": "normalmodus an",  # Unverändert, Befehl wird durchgelassen
        "zurück auf normal": "normalmodus an",  # Umwandeln in den gleichen Befehl wie oben
        "urlaubs modus": "urlaubsmodus",
        "temperatur wohnzimmer": "temperatur wohnzimmer",  # Für Temperaturabfrage
    }
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    return text.strip()


def remove_fuellwoerter(text):
    fuellwoerter = [
        "bitte", "mach", "mache", "kannst", "du", "das", "den", "die",
        "in", "wer", "im", "der", "lade", "nordlicht", "fahre", "ihre", "farbe",
    ]
    return " ".join([w for w in text.split() if w not in fuellwoerter])


def auto_ergaenze_rollade(text):
    bewegung_woerter = ["raus", "rein", "runter", "unter", "rauf", "hoch", "auf"]
    rollo_begriffe = ["rollade", "rollo", "rollladen", "rolladen"]
    if not any(w in text for w in rollo_begriffe):
        for wort in bewegung_woerter:
            if wort in text.split():
                print("🧠 Ergänze fehlendes Gerät: Rollade")
                return text.replace(wort, f"rollade {wort}")
    return text


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


def clean_text(user_input):
    print(f"🎧 Original: {user_input}")
    text = normalize_text(user_input)
    text = remove_fuellwoerter(text)
    print(f"🧹 Gefiltert: {text}")
    text = auto_ergaenze_rollade(text)
    text = ersetze_zahlwoerter(text)
    print(f"✅ Ergebnis: {text}")
    return text
