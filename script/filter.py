# /opt/script/filter.py

def normalize_text(text):
    corrections = {
        "ron t r": "runter",
        "ronter": "runter",
        "unter": "runter",
        "darunter": "runter",
        "darrunter": "runter",
        "rrunter": "runter",          # 👈 NEU!
        "hochher": "hoch",
        "man": "",
        "rolle": "rollade",
        "roller": "rollade",
        "rollladen": "rollade",
        "rollo": "rollade",
    }
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    return text.strip()


def remove_fuellwoerter(text):
    fuellwoerter = [
        "bitte", "mach", "mache", "kannst", "du", "das", "den", "die",
        "in", "wer", "im", "der", "lade", "fahre", "ihre", "farbe",
    ]
    return " ".join([w for w in text.split() if w not in fuellwoerter])


def auto_ergaenze_rollade(text):
        bewegung_woerter = ["runter", "unter", "rauf", "hoch", "auf"]
        rollo_begriffe = ["rollade", "rollo", "rollladen", "rolladen"]
        if not any(w in text for w in rollo_begriffe):
            for wort in bewegung_woerter:
                if wort in text.split():
                    print("🧠 Ergänze fehlendes Gerät: Rollade")
                    return text.replace(wort, f"rollade {wort}")
        return text
    


def clean_text(user_input):
    print(f"🎧 Original: {user_input}")
    text = normalize_text(user_input)
    text = remove_fuellwoerter(text)
    print(f"🧹 Gefiltert: {text}")
    text = auto_ergaenze_rollade(text)
    print(f"✅ Ergebnis: {text}")
    return text
