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


TEMPLATE = "templates/JACQUEMUSS.png"
OUTPUT   = "final/jacquemus"


async def generate(fields, is_free):
    nom = fields["nom"]
    taille = fields["taille"]
    couleur = fields["couleur"]
    ref = fields["ref"]
    prix = fields["prix"]
    rdm = random.randint(1, 999999)
    out = f"{OUTPUT}_{rdm}.png"
    os.makedirs("final", exist_ok=True)
    img = Image.open(TEMPLATE).convert("RGB")
    draw = ImageDraw.Draw(img)
    W = img.width

    f1 = ImageFont.truetype("calibri-font-family/LiberationSerif-Bold.ttf", 18)
    f2 = ImageFont.truetype("calibri-font-family/LiberationSerif-Regular.ttf", 18)

    # Layer 1: field
    _txt0 = nom
    t(draw, (W // 2 + int(-400 * 1), int(600 * 1)), _txt0, f1, (0, 0, 0), 4)

    # Layer 2: formula
    _txt1 = f"REF : {ref}\nCouleur : {couleur}\nTaille : {taille}"
    t(draw, (W // 2 + int(-400 * 1), int(621 * 1)), _txt1, f2, (0, 0, 0), 4)

    # Layer 3: random_text
    _txt2 = f"Commandes : {random.randint(1000000000, 9999999999)}\nFacture : {random.randint(1000000000, 9999999999)}\nPass\xe9e le : {random.choice(MOIS_FR)} {random.randint(1, 28)} {random.randint(2021, 2023)}"
    t(draw, (W // 2 + int(195 * 1), int(245 * 1)), _txt2, f1, (0, 0, 0), 4)

    # Layer 4: random_text
    _txt3 = f"{prenom()} {prenom()}\n{random.randint(1, 200)} {random.choice(TYPES_ROUTE)} {random.choice(NOMS_ROUTE)}\nAppartement {random.randint(1, 300)}\n{(lambda v: VILLES[v] + " " + v)(random.choice(list(VILLES.keys())))}\nFRANCE\nT. : 0{random.randint(6, 7)}{random.randint(10000000, 99999999)}"
    t(draw, (W // 2 + int(-400 * 1), int(220 * 1)), _txt3, f2, (0, 0, 0), 4)

    # Layer 5: formula
    _txt4 = f"\u20ac{prix:.2f}"
    t(draw, (W // 2 + int(61 * 1), int(643 * 1)), _txt4, f2, (0, 0, 0), 4)

    # Layer 6: formula
    _txt5 = f"\u20ac{prix:.2f}"
    t(draw, (W // 2 + int(320 * 1), int(643 * 1)), _txt5, f1, (0, 0, 0), 4)

    # Layer 7: formula
    ht = float(prix)*0.833333
    tva = float(prix)*0.16666
    _txt6 = f"\u20ac{ht:.2f}\n\u20ac{tva:.2f}\nGratuit\n\u20ac{prix}"
    t(draw, (W // 2 + int(340 * 1), int(745 * 1)), _txt6, f1, (0, 0, 0), 4)

    img.save(out, "PNG")
    return out