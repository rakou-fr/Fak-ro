# -*- coding: utf-8 -*-
import os
import random
from PIL import Image, ImageDraw, ImageFont

TEMPLATE = "templates/apple_template.png"
OUTPUT   = "final/apple"

# W=1191 H=1691
W = 1191

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
NOMS = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand",
    "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy",
    "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard", "Bonnet",
    "Dupont", "Lambert", "Fontaine", "Rousseau", "Vincent", "Muller",
    "Lefevre", "Faure", "Andre", "Mercier", "Blanc", "Guerin", "Boyer",
    "Garnier", "Chevalier", "Francois", "Legrand", "Gauthier", "Garcia",
]


def prenom():
    return random.choice(PRENOMS)

def nom():
    return random.choice(NOMS).upper()

def adresse_client():
    p = prenom()
    n = nom()
    numero = random.randint(1, 200)
    route = random.choice(TYPES_ROUTE)
    nom_rue = random.choice(NOMS_ROUTE)
    ville = random.choice(list(VILLES.keys()))
    cp = VILLES[ville]
    return f"{p} {n}", f"{numero} {route} {nom_rue}", f"{cp} {ville.upper()}"


def t(draw, pos, text, font, color=(0, 0, 0), spacing=4):
    draw.text(pos, text, font=font, fill=color, spacing=spacing)


async def generate(fields, is_free):
    desc  = fields["desc"]
    prix  = fields["prix"]
    date  = fields["date"]

    prix_f  = float(prix)
    ht      = prix_f / 1.20
    tva     = prix_f - ht
    ttc     = prix_f
    num_fac = f"2023-{random.randint(100000, 999999)}"
    engagement = f"BC{random.randint(1000, 9999)}"
    code_svc   = f"PRFG{random.randint(10000, 99999)}"

    # Adresse client
    nom_client, rue_client, cp_ville_client = adresse_client()

    rdm = random.randint(1, 999999)
    out = f"{OUTPUT}_{rdm}.png"
    os.makedirs("final", exist_ok=True)

    img  = Image.open(TEMPLATE).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Polices - utilise LiberationSans qui supporte bien Unicode
    REG  = "calibri-font-family/LiberationSans-Regular.ttf"
    BOLD = "calibri-font-family/LiberationSans-Bold.ttf"

    f11  = ImageFont.truetype(REG,  11)
    f12  = ImageFont.truetype(REG,  12)
    f13  = ImageFont.truetype(REG,  13)
    f13b = ImageFont.truetype(BOLD, 13)
    f14  = ImageFont.truetype(REG,  14)
    f14b = ImageFont.truetype(BOLD, 14)
    f20b = ImageFont.truetype(BOLD, 20)

    C = (0, 0, 0)
    CG = (80, 80, 80)

    # -- Numero de facture (en haut a droite apres "FACTURE - ")
    # "FACTURE -" est deja sur le template, on ajoute juste le numero
    t(draw, (710, 30), num_fac, f20b, C)

    # -- Dates (a droite, sous le titre)
    t(draw, (820, 68),  date, f13, C)   # Date de facturation
    t(draw, (820, 85),  date, f13, C)   # Echeance (meme date pour simplifier)

    # -- Adresse client (colonne droite, zone "Andriy ZEMOURI")
    t(draw, (630, 175), nom_client,      f13b, C)
    t(draw, (630, 193), rue_client,      f13,  C)
    t(draw, (630, 210), cp_ville_client, f13,  C)

    # -- Ligne tableau produit
    # Description (colonne gauche)
    t(draw, (28, 535), desc, f13, C)
    # Type de produit
    t(draw, (290, 535), "Biens", f13, C)
    # Date
    t(draw, (390, 535), date, f13, C)
    # Qte
    t(draw, (455, 535), "1,00", f13, C)
    # Unite
    t(draw, (497, 535), "h", f13, C)
    # Prix unitaire HT
    t(draw, (545, 535), f"{ht:.2f} \u20ac", f13, C)
    # TVA
    t(draw, (655, 535), "20,00 %", f13, C)
    # Montant TTC
    t(draw, (720, 535), f"{ttc:.2f} \u20ac", f13, C)

    # -- Totaux (bas droite)
    t(draw, (870, 620), f"{ht:.2f} \u20ac",  f13b, C)   # Total HT
    t(draw, (870, 638), f"{tva:.2f} \u20ac", f13,  C)   # TVA 20%
    t(draw, (870, 660), f"{ttc:.2f} \u20ac", f14b, C)   # Total TTC

    # -- Conditions paiement / engagement / code service
    t(draw, (175, 720), "30 jours",   f13, C)
    t(draw, (175, 738), engagement,   f13, C)
    t(draw, (175, 756), code_svc,     f13, C)

    img.save(out, "PNG")
    return out