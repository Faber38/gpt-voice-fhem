RICHTUNGEN = [
    "Norden", "Nord-Nordost", "Nordost", "Ost-Nordost", "Osten",
    "Ost-Südost", "Südost", "Süd-Südost", "Süden", "Süd-Südwest",
    "Südwest", "West-Südwest", "Westen", "West-Nordwest", "Nordwest", "Nord-Nordwest"
]

def windrichtung_text(degrees):
    index = int((degrees + 11.25) / 22.5) % 16
    richtung = RICHTUNGEN[index]
    print(f"🧭 Windrichtung aus {degrees}° → {richtung}")
    return richtung

def uebersetze_warnung(text):
    ersetzungen = [
        ("There is a risk of wind gusts", "Es besteht die Gefahr von Sturmböen"),
        ("Achtung: wind gusts", "Achtung: Sturmböen"),
        ("wind gusts", "Sturmböen"),
        ("level 1 of 4", "Stufe 1 von 4"),
        ("level 2 of 4", "Stufe 2 von 4"),
        ("level 3 of 4", "Stufe 3 von 4"),
        ("level 4 of 4", "Stufe 4 von 4"),
    ]
    for englisch, deutsch in ersetzungen:
        text = text.replace(englisch, deutsch)
    text = text.replace("(", "").replace(")", "")
    return text

def erklaere_sturmböen(text):
    stufen_info = {
        "Stufe 1 von 4": ("50 bis 60 Stundenkilometern", "Diese Stufe gilt als harmlos."),
        "Stufe 2 von 4": ("60 bis 80 Stundenkilometern", "Es besteht Gefahr durch herabfallende Äste oder lose Gegenstände."),
        "Stufe 3 von 4": ("80 bis 100 Stundenkilometern", "Es drohen Schäden an Bäumen, Dächern oder Fahrzeugen."),
        "Stufe 4 von 4": ("über 100 Stundenkilometern", "Es besteht akute Orkangefahr mit hohem Schadenspotenzial.")
    }
    for stufe, (kmh, bedeutung) in stufen_info.items():
        if stufe in text:
            erklaerung = f" Das entspricht etwa {kmh}. {bedeutung}"
            return text + erklaerung
    return text
