# -*- coding: utf-8 -*-
import os
import random
from PIL import Image, ImageDraw, ImageFont

VILLES = {{
    'Paris': '75000', 'Marseille': '13000', 'Lyon': '69000',
    'Toulouse': '31000', 'Nice': '06000', 'Nantes': '44000',
    'Strasbourg': '67000', 'Montpellier': '34000', 'Bordeaux': '33000',
    'Lille': '59000', 'Rennes': '35000', 'Reims': '51100',
    'Le Havre': '76600', 'Saint-\u00c9tienne': '42000', 'Toulon': '83000',
    'Grenoble': '38000', 'Dijon': '21000', 'Angers': '49000',
    'N\u00eemes': '30000', 'Le Mans': '72000',
}}
TYPES_ROUTE = ["Rue", "Avenue", "Boulevard", "Chemin", "Impasse"]
NOMS_ROUTE  = [
    "de la Libert\u00e9", "des Roses", "du Moulin", "de la Paix", "des Champs",
    "du Soleil", "de l'Avenir", "de la Joie", "des \u00c9toiles", "du Ciel",
    "de la Cascade", "du Ruisseau", "de la Montagne", "du Lac", "du Printemps",
    "de la Brise", "des Nuages", "de la Rivi\u00e8re", "de la For\u00eat",
    "de l'Oc\u00e9an", "de la Plage", "du Vent", "de l'Horizon", "des Collines",
    "de l'Espoir", "de la S\u00e9r\u00e9nit\u00e9", "du Z\u00e9nith", "de l'Automne",
    "de la Vie", "de la Lumi\u00e8re", "des Oiseaux", "de la Neige",
]
PRENOMS = [
    "Lucas", "Emma", "Nathan", "Jade", "Hugo", "Lena", "Tom", "Chloe",
    "Mathis", "Camille", "Alexis", "Manon", "Theo", "Lea", "Antoine",
    "Sarah", "Romain", "Julie", "Nicolas", "Marine", "Pierre", "Laura",
    "Julien", "Alice", "Baptiste", "Pauline", "Maxime", "Lucie", "Thomas",
    "Oceane", "Clement", "Margot", "Quentin", "Amelie", "Adrien", "Elise",
    "Kevin", "Charlotte", "Dylan", "Anais", "Amine", "Yasmine", "Karim",
    "Fatima", "Mohamed", "Nadia", "Youssef", "Sofia", "Bilal", "In\u00e8s",
]
LETTRES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
MOIS_FR = ["janvier", "f\u00e9vrier", "mars", "avril", "mai", "juin",
           "juillet", "ao\u00fbt", "septembre", "octobre", "novembre", "d\u00e9cembre"]


def prenom():
    return random.choice(PRENOMS)

def adresse():
    p1 = prenom(); p2 = prenom()
    num = random.randint(1, 200)
    route = random.choice(TYPES_ROUTE)
    nom = random.choice(NOMS_ROUTE)
    ville = random.choice(list(VILLES.keys()))
    cp = VILLES[ville]
    return f"{{p1}} {{p2}}\n{{num}} {{route}} {{nom}}\n{{cp}} {{ville}}\nFRANCE"

def wrap(text, max_len):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_len:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return "\n".join(lines)

def t(draw, pos, text, font, color, spacing=4):
    draw.text(pos, text, font=font, fill=color, spacing=spacing)

def t_right(draw, pos, text, font, color, spacing=4):
    lines = text.split("\n")
    max_w = max(draw.textlength(l, font=font) for l in lines)
    x, y = pos
    for line in lines:
        lw = draw.textlength(line, font=font)
        draw.text((x + max_w - lw, y + spacing), line, font=font, fill=color, spacing=spacing)
        h = font.getbbox(line)[3] - font.getbbox(line)[1]
        y += h + spacing

def t_left(draw, pos, text, font, color, spacing=4):
    lines = text.split("\n")
    x, y = pos
    for line in lines:
        lw = draw.textlength(line, font=font)
        draw.text((x - lw, y), line, font=font, fill=color, spacing=spacing)
        h = font.getbbox(line)[3] - font.getbbox(line)[1]
        y += h + spacing


TEMPLATE = "templates/Farfetch-1.png"
OUTPUT   = "final/farfetch"


async def generate(fields, is_free):
    date = fields["date"]
    id_far = fields["id_far"]
    id_marque = fields["id_marque"]
    desc = fields["desc"]
    prix = fields["prix"]
    compo = fields["compo"]
    pays = fields["pays"]
    rdm = random.randint(1, 999999)
    out = f"{OUTPUT}_{rdm}.png"
    os.makedirs("final", exist_ok=True)
    img = Image.open(TEMPLATE).convert("RGB")
    draw = ImageDraw.Draw(img)
    W = img.width

    f1 = ImageFont.truetype("calibri-font-family/calibri-Regular.ttf", 29)
    f2 = ImageFont.truetype("calibri-font-family/calibri-bold.ttf", 28)
    f3 = ImageFont.truetype("calibri-font-family/calibri-regular.ttf", 28)

    # Layer 1: random_address
    _txt0 = adresse()
    t(draw, (W // 2 + int(-800 * 1), int(950 * 1)), _txt0, f1, (9, 9, 9), 4)

    # Layer 2: random_address
    _txt1 = adresse()
    t(draw, (W // 2 + int(18 * 1), int(950 * 1)), _txt1, f1, (9, 9, 9), 4)

    # Layer 3: field
    _txt2 = date
    t(draw, (W // 2 + int(-650 * 1), int(572 * 1)), _txt2, f2, (9, 9, 9), 4)

    # Layer 4: random_text
    _txt3 = f"IT{random.randint(100000000000, 999999999999)}"
    t(draw, (W // 2 + int(-640 * 1), int(540 * 1)), _txt3, f2, (9, 9, 9), 4)

    # Layer 5: random_text
    _txt4 = f"AGDENC{random.randint(100000000, 999999999)}"
    t(draw, (W // 2 + int(195 * 1), int(571 * 1)), _txt4, f2, (9, 9, 9), 4)

    # Layer 6: random_text
    _txt5 = f"0{random.randint(1000, 9999)}F{random.randint(100000000, 999999999)}F001"
    t(draw, (W // 2 + int(20 * 1), int(768 * 1)), _txt5, f2, (9, 9, 9), 4)

    # Layer 7: random_text
    _txt6 = f"ITDN000{random.randint(10000, 99999)}"
    t(draw, (W // 2 + int(-610 * 1), int(605 * 1)), _txt6, f2, (9, 9, 9), 4)

    # Layer 8: random_text
    _txt7 = f"NL{random.randint(100000000, 999999999)}"
    t(draw, (W // 2 + int(-635 * 1), int(637 * 1)), _txt7, f2, (9, 9, 9), 4)

    # Layer 9: formula
    _txt8 = f"{prix:.2f}"
    t(draw, (W // 2 + int(-285 * 1), int(1278 * 1)), _txt8, f3, (9, 9, 9), 4)

    # Layer 10: formula
    _txt9 = f"{prix:.2f}"
    t(draw, (W // 2 + int(-8 * 1), int(1278 * 1)), _txt9, f3, (9, 9, 9), 4)

    # Layer 11: formula
    _txt10 = f"{prix:.2f}"
    t(draw, (W // 2 + int(192 * 1), int(1278 * 1)), _txt10, f3, (9, 9, 9), 4)

    # Layer 12: field
    _txt11 = wrap(compo, 18)
    t(draw, (W // 2 + int(295 * 1), int(1278 * 1)), _txt11, f3, (9, 9, 9), 4)

    # Layer 13: formula
    _txt12 = f"{id_far} {desc} {id_marque}"
    t(draw, (W // 2 + int(-800 * 1), int(1278 * 1)), _txt12, f3, (9, 9, 9), 4)

    # Layer 14: field
    _txt13 = pays
    t(draw, (W // 2 + int(515 * 1), int(1278 * 1)), _txt13, f3, (9, 9, 9), 4)

    # Layer 15: formula
    _txt14 = f"{prix:.2f}"
    t(draw, (W // 2 + int(-8 * 1), int(1438 * 1)), _txt14, f2, (9, 9, 9), 4)

    # Layer 16: formula
    _txt15 = f"{prix:.2f}"
    t(draw, (W // 2 + int(192 * 1), int(1438 * 1)), _txt15, f2, (9, 9, 9), 4)

    # Layer 17: formula
    _txt16 = f"{prix:.2f}"
    t(draw, (W // 2 + int(-285 * 1), int(1438 * 1)), _txt16, f2, (9, 9, 9), 4)

    # Layer 18: formula
    _txt17 = f"{prix:.2f}"
    t(draw, (W // 2 + int(125 * 1), int(1650 * 1)), _txt17, f3, (9, 9, 9), 4)

    # Layer 19: formula
    _txt18 = f"{prix:.2f}"
    t(draw, (W // 2 + int(-380 * 1), int(1650 * 1)), _txt18, f3, (9, 9, 9), 4)

    # Layer 20: formula
    _txt19 = f"{prix:.2f}"
    t(draw, (W // 2 + int(125 * 1), int(1683 * 1)), _txt19, f2, (9, 9, 9), 4)

    # Layer 21: formula
    _txt20 = f"{prix:.2f}"
    t(draw, (W // 2 + int(-380 * 1), int(1683 * 1)), _txt20, f2, (9, 9, 9), 4)

    img.save(out, "PNG")
    return out