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


TEMPLATE = "templates/Goyard.png"
OUTPUT   = "final/goyard"


async def generate(fields, is_free):
    date = fields["date"]
    designation = fields["designation"]
    prix = fields["prix"]
    rdm = random.randint(1, 999999)
    out = f"{OUTPUT}_{rdm}.png"
    os.makedirs("final", exist_ok=True)
    img = Image.open(TEMPLATE).convert("RGB")
    draw = ImageDraw.Draw(img)
    W = img.width

    f1 = ImageFont.truetype("calibri-font-family/calibri-bold.ttf", 33)
    f2 = ImageFont.truetype("calibri-font-family/calibri-Regular.ttf", 32)
    f3 = ImageFont.truetype("calibri-font-family/calibri-Bold.ttf", 33)
    f4 = ImageFont.truetype("calibri-font-family/calibri-regular.ttf", 33)

    # Layer 1: random_text
    _txt0 = f"{prenom()} {prenom()}"
    t(draw, (W // 2 + int(-725 * 1), int(490 * 1)), _txt0, f1, (0, 0, 0), 4)

    # Layer 2: random_address
    _txt1 = adresse()
    t(draw, (W // 2 + int(-725 * 1), int(490 * 1)), _txt1, f2, (0, 0, 0), 4)

    # Layer 3: field
    _txt2 = date
    t(draw, (W // 2 + int(522 * 1), int(787 * 1)), _txt2, f3, (0, 0, 0), 4)

    # Layer 4: field
    _txt3 = date
    t(draw, (W // 2 + int(-650 * 1), int(787 * 1)), _txt3, f4, (0, 0, 0), 4)

    # Layer 5: random_text
    _txt4 = f"{prenom()}"
    t(draw, (W // 2 + int(-408 * 1), int(746 * 1)), _txt4, f4, (0, 0, 0), 4)

    # Layer 6: random_text
    _txt5 = f"{random.randint(100, 999)} {random.randint(100, 999)}"
    t(draw, (W // 2 + int(575 * 1), int(746 * 1)), _txt5, f3, (0, 0, 0), 4)

    # Layer 7: field
    _txt6 = designation
    t(draw, (W // 2 + int(-705 * 1), int(962 * 1)), _txt6, f4, (0, 0, 0), 4)

    # Layer 8: formula
    _txt7 = f"1                           20.00%"
    t(draw, (W // 2 + int(-26 * 1), int(962 * 1)), _txt7, f4, (0, 0, 0), 4)

    # Layer 9: formula
    ht = float(prix)*0.8333333
    _txt8 = f"{ht:.2f}"
    t(draw, (W // 2 + int(45 * 1), int(962 * 1)), _txt8, f4, (0, 0, 0), 4)

    # Layer 10: formula
    _txt9 = f"{prix:.2f}"
    t(draw, (W // 2 + int(310 * 1), int(962 * 1)), _txt9, f4, (0, 0, 0), 4)

    # Layer 11: formula
    _txt10 = f"{prix:.2f}"
    t(draw, (W // 2 + int(505 * 1), int(962 * 1)), _txt10, f4, (0, 0, 0), 4)

    # Layer 12: formula
    _txt11 = f"{prix:.2f}"
    t(draw, (W // 2 + int(-170 * 1), int(1729 * 1)), _txt11, f4, (0, 0, 0), 4)

    # Layer 13: formula
    ht = float(prix)*0.8333333
    _txt12 = f"{ht:.2f}"
    t(draw, (W // 2 + int(130 * 1), int(1729 * 1)), _txt12, f4, (0, 0, 0), 4)

    # Layer 14: formula
    tva = float(prix)*0.16666666
    _txt13 = f"{tva:.2f}"
    t(draw, (W // 2 + int(373 * 1), int(1729 * 1)), _txt13, f4, (0, 0, 0), 4)

    # Layer 15: formula
    ht = float(prix)*0.83333333
    _txt14 = f"{ht:.2f}"
    t(draw, (W // 2 + int(155 * 1), int(1913 * 1)), _txt14, f4, (0, 0, 0), 4)

    # Layer 16: formula
    _txt15 = f"{prix:.2f}\n\n\n{prix:.2f}"
    t(draw, (W // 2 + int(450 * 1), int(1913 * 1)), _txt15, f4, (0, 0, 0), 4)

    img.save(out, "PNG")
    return out