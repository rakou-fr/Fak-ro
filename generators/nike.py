# -*- coding: utf-8 -*-
"""
templates/nike.py — Template facture Nike (migré depuis generators/nike.py)

Utilise assets/templates/nike.png comme fond.
Logique 100% fidèle à l'original : coordonnées scale×2, adresse aléatoire,
calcul HT/TVA automatique.

Champs attendus (formulaire Discord) :
    prix  → Prix TTC sans décimales (ex: 129)
    desc  → Description du produit
    qte   → Quantité
    date  → Date (ex: 01/01/2025)
"""

from __future__ import annotations

import random

from PIL import Image, ImageDraw

from template_base import BaseTemplate, ASSETS

# ── Données aléatoires ────────────────────────────────────────────────────────

VILLES = {
    'Paris': '75000', 'Marseille': '13000', 'Lyon': '69000',
    'Toulouse': '31000', 'Nice': '06000', 'Nantes': '44000',
    'Strasbourg': '67000', 'Montpellier': '34000', 'Bordeaux': '33000',
    'Lille': '59000', 'Rennes': '35000', 'Reims': '51100',
    'Le Havre': '76600', 'Saint-Étienne': '42000', 'Toulon': '83000',
    'Grenoble': '38000', 'Dijon': '21000', 'Angers': '49000',
    'Nîmes': '30000', 'Le Mans': '72000',
}
TYPES_ROUTE = ["Rue", "Avenue", "Boulevard", "Chemin", "Impasse"]
NOMS_ROUTE  = [
    "de la Liberté", "des Roses", "du Moulin", "de la Paix", "des Champs",
    "du Soleil", "de l'Avenir", "de la Joie", "des Étoiles", "du Ciel",
    "de la Cascade", "du Ruisseau", "de la Montagne", "du Lac", "du Printemps",
    "de la Brise", "des Nuages", "de la Rivière", "de la Forêt",
    "de l'Océan", "de la Plage", "du Vent", "de l'Horizon", "des Collines",
    "de l'Espoir", "de la Sérénité", "du Zénith", "de l'Automne",
    "de la Vie", "de la Lumière", "des Oiseaux", "de la Neige",
]
PRENOMS = [
    "Lucas", "Emma", "Nathan", "Jade", "Hugo", "Lena", "Tom", "Chloe",
    "Mathis", "Camille", "Alexis", "Manon", "Theo", "Lea", "Antoine",
    "Sarah", "Romain", "Julie", "Nicolas", "Marine", "Pierre", "Laura",
    "Julien", "Alice", "Baptiste", "Pauline", "Maxime", "Lucie", "Thomas",
    "Oceane", "Clement", "Margot", "Quentin", "Amelie", "Adrien", "Elise",
    "Kevin", "Charlotte", "Dylan", "Anais", "Amine", "Yasmine", "Karim",
    "Fatima", "Mohamed", "Nadia", "Youssef", "Sofia", "Bilal", "Inès",
]


def _prenom() -> str:
    return random.choice(PRENOMS)


def _adresse() -> str:
    num   = random.randint(1, 200)
    route = random.choice(TYPES_ROUTE)
    nom   = random.choice(NOMS_ROUTE)
    ville = random.choice(list(VILLES.keys()))
    cp    = VILLES[ville]
    return f"{_prenom()} {_prenom()}\n{num} {route} {nom}\n{cp} {ville}\nFRANCE"


# ── Template ──────────────────────────────────────────────────────────────────

class NikeTemplate(BaseTemplate):

    KEY   = "NIKE"
    LABEL = "Nike"
    FIELDS = [
        {"id": "prix", "label": "Prix TTC (sans décimales)", "placeholder": "129"},
        {"id": "desc", "label": "Description du produit",   "placeholder": "Nike Air Max 90 White Black"},
        {"id": "qte",  "label": "Quantité",                 "placeholder": "1"},
        {"id": "date", "label": "Date",                     "placeholder": "01/01/2025"},
    ]

    # Chemin vers le .png de fond (dans assets/templates/)
    TEMPLATE_FILE = str(ASSETS / "templates" / "nike.png")
    # Police (dans assets/fonts/)
    BOLD_FONT     = "calibri-bold.ttf"
    # Couleur texte principale
    C             = (54, 54, 54)

    async def generate(self, fields: dict, is_free: bool) -> str:
        prix = fields["prix"]
        desc = fields["desc"]
        qte  = fields["qte"]
        date = fields["date"]

        prix_ht = int(float(prix) / 1.20)
        tva     = float(prix) - float(prix) / 1.2

        img  = Image.open(self.TEMPLATE_FILE).convert("RGB")
        draw = ImageDraw.Draw(img)
        W    = img.width  # 1536

        # Même système de coordonnées que l'original (scale=2)
        def pos(x_off, y, scale=2):
            return (W // 2 + int(x_off * scale), int(y * scale))

        f22 = self.font(self.BOLD_FONT, 22)

        def t(p, text, spacing=4):
            draw.text(p, text, font=f22, fill=self.C, spacing=spacing)

        # Numéro facture / commande
        t(pos(-203, 93),  f"FR{random.randint(1000000000, 9999999999)}")
        t(pos(-203, 105), f"CDD{random.randint(100000000, 999999999)}")

        # Dates
        t(pos(-203, 153), date)
        t(pos(-203, 177), date)

        # Adresses (générées aléatoirement)
        t(pos(120, 90),  _adresse())
        t(pos(120, 150), _adresse())

        # Numéro produit
        t(pos(-339, 347), f"DM{random.randint(1000, 9999)}")

        # Description avec word-wrap à 30 caractères
        words, lines, cur = desc.split(), [], ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > 30:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        t(pos(-202, 347), "\n".join(lines))

        # Quantités
        t(pos(-8, 357), f"{qte},00\n\n\n{qte}")

        # Prix brut / HT / total
        t(pos(45,  357), f"{prix},99 €\n\n\n0,00 €")
        t(pos(175, 357), f"{prix_ht},99 €\n\n\n0,00 €")
        t(pos(240, 357), f"{prix},99 €\n\n\n0,00 €")

        # Récap bas de page
        t(pos(-20, 699), "Total Hors TVA:\nTVA:\n\nMontant Total de la Facture:\n\nMode(s) de Paiement:                 Carte de Crédit")
        t(pos(297, 699), f"{prix},99 €\n{tva:.0f},00 €\n\n{prix},99 €\n\n{prix},00 €")

        if is_free:
            img = self.add_watermark(img)

        return self.save(img)