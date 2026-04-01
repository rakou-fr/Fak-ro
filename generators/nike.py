# -*- coding: utf-8 -*-
import os
import random
from PIL import Image, ImageDraw, ImageFont

TEMPLATE = "templates/nike.png"
OUTPUT   = "final/nike"
BOLD     = "calibri-font-family/calibri-bold.ttf"
C        = (54, 54, 54)

VILLES = {
    'Paris': '75000', 'Marseille': '13000', 'Lyon': '69000',
    'Toulouse': '31000', 'Nice': '06000', 'Nantes': '44000',
    'Strasbourg': '67000', 'Montpellier': '34000', 'Bordeaux': '33000',
    'Lille': '59000', 'Rennes': '35000', 'Reims': '51100',
    'Le Havre': '76600', 'Saint-\u00c9tienne': '42000', 'Toulon': '83000',
    'Grenoble': '38000', 'Dijon': '21000', 'Angers': '49000',
    'N\u00eemes': '30000', 'Le Mans': '72000',
}
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


def prenom():
    return random.choice(PRENOMS)


def adresse():
    p1     = prenom()
    p2     = prenom()
    num    = random.randint(1, 200)
    route  = random.choice(TYPES_ROUTE)
    nom    = random.choice(NOMS_ROUTE)
    ville  = random.choice(list(VILLES.keys()))
    cp     = VILLES[ville]
    return f"{p1} {p2}\n{num} {route} {nom}\n{cp} {ville}\nFRANCE"


def t(draw, pos, text, font, color=C, spacing=4):
    draw.text(pos, text, font=font, fill=color, spacing=spacing)


async def generate(fields, is_free):
    prix = fields["prix"]
    desc = fields["desc"]
    qte  = fields["qte"]
    date = fields["date"]

    prix_ht = int(float(prix) / 1.20)
    tva     = float(prix) - float(prix) / 1.2

    rdm = random.randint(1, 999999)
    out = f"{OUTPUT}_{rdm}.png"
    os.makedirs("final", exist_ok=True)

    img  = Image.open(TEMPLATE).convert("RGB")
    draw = ImageDraw.Draw(img)
    W    = img.width  # 1536

    def pos(x_off, y, scale=2):
        return (W // 2 + int(x_off * scale), int(y * scale))

    f22 = ImageFont.truetype(BOLD, 22)

    # Numero facture
    t(draw, pos(-203, 93),  f"FR{random.randint(1000000000, 9999999999)}", f22)
    # Numero commande
    t(draw, pos(-203, 105), f"CDD{random.randint(100000000, 999999999)}", f22)
    # Dates
    t(draw, pos(-203, 153), date, f22)
    t(draw, pos(-203, 177), date, f22)
    # Adresses
    t(draw, pos(120, 90),  adresse(), f22)
    t(draw, pos(120, 150), adresse(), f22)
    # Numero produit
    t(draw, pos(-339, 347), f"DM{random.randint(1000, 9999)}", f22)

    # Description (wrap a 30 chars)
    words, lines, cur = desc.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > 30:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    t(draw, pos(-202, 347), "\n".join(lines), f22)

    # Quantites
    t(draw, pos(-8, 357),  f"{qte},00\n\n\n{qte}", f22)
    # Prix brut
    t(draw, pos(45, 357),  f"{prix},99 \u20ac\n\n\n0,00 \u20ac", f22)
    # Prix HT
    t(draw, pos(175, 357), f"{prix_ht},99 \u20ac\n\n\n0,00 \u20ac", f22)
    # Prix total
    t(draw, pos(240, 357), f"{prix},99 \u20ac\n\n\n0,00 \u20ac", f22)

    # Recap bas
    t(draw, pos(297, 699), f"{prix},99 \u20ac\n{tva:.0f},00 \u20ac\n\n{prix},99 \u20ac\n\n{prix},00 \u20ac", f22)
    t(draw, pos(-20, 699), "Total Hors TVA:\nTVA:\n\nMontant Total de la Facture:\n\nMode(s) de Paiement:                 Carte de Cr\u00e9dit", f22)

    img.save(out, "PNG")
    return out
