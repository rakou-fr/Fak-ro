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


TEMPLATE = "templates/burberry.png"
OUTPUT   = "final/burberry"


async def generate(fields, is_free):
    num = fields["num"]
    desc = fields["desc"]
    prix = fields["prix"]
    qte = fields["qte"]
    rdm = random.randint(1, 999999)
    out = f"{OUTPUT}_{rdm}.png"
    os.makedirs("final", exist_ok=True)
    img = Image.open(TEMPLATE).convert("RGB")
    draw = ImageDraw.Draw(img)
    W = img.width

    f1 = ImageFont.truetype("calibri-font-family/LibreBaskerville-Bold.ttf", 13)
    f2 = ImageFont.truetype("calibri-font-family/LibreBaskerville-Bold.ttf", 15)
    f3 = ImageFont.truetype("calibri-font-family/LibreBaskerville-Bold.ttf", 11)

    # Layer 1: field
    _txt0 = num
    t(draw, (W // 2 + int(-348 * 1), int(397 * 1)), _txt0, f1, (27, 27, 27), 4)

    # Layer 2: formula
    _txt1 = f"{num}                  {random.randint(10, 28)}/0{random.randint(1, 9)}/{random.randint(2020, 2023)} - {random.randint(10, 23)} : {random.randint(10, 59)}"
    t(draw, (W // 2 + int(-138 * 1), int(332 * 1)), _txt1, f2, (27, 27, 27), 4)

    # Layer 3: field
    _txt2 = wrap(desc, 16)
    t(draw, (W // 2 + int(-275 * 1), int(392 * 1)), _txt2, f1, (27, 27, 27), 4)

    # Layer 4: formula
    ht = float(prix)*0.833
    tva = float(prix)-float(prix)*0.833
    _txt3 = f"{qte}                     {ht:.3f}       20.00%      {tva:.2f}         {ht:.3f}                 {prix}.00"
    t(draw, (W // 2 + int(-125 * 1), int(397 * 1)), _txt3, f1, (27, 27, 27), 4)

    # Layer 5: formula
    _txt4 = f"TOTAL H.T :                                       EUR\nTOTAL TVA :                                     EUR\nTOTAL TTC :                                     EUR\n\n                                                                      EUR\n\n                                                                      EUR"
    t(draw, (W // 2 + int(75 * 1), int(474 * 1)), _txt4, f1, (24, 24, 24), 4)

    # Layer 6: formula
    ht = float(prix)*0.833
    tva = float(prix)-float(prix)*0.833
    _txt5 = f"{ht:.3f}\n{tva:.2f}\n{prix}.00\n\n{prix}.00\n\n0.00"
    t(draw, (W // 2 + int(218 * 1), int(474 * 1)), _txt5, f1, (27, 27, 27), 4)

    # Layer 7: random_text
    _txt6 = f"Vendeur :             {prenom()} {random.choice(LETTRES)}.\nENC CB{random.randint(10, 99)}"
    t(draw, (W // 2 + int(-352 * 1), int(715 * 1)), _txt6, f3, (27, 27, 27), 4)

    img.save(out, "PNG")
    return out