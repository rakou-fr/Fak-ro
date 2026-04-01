import random

PRENOMS = [
    "Lucas", "Hugo", "Nathan", "Tom", "Théo", "Maxime", "Léo", "Arthur",
    "Louis", "Raphaël", "Ethan", "Alexis", "Antoine", "Baptiste", "Clément",
    "Emma", "Léa", "Chloé", "Camille", "Inès", "Manon", "Jade", "Lucie",
    "Sarah", "Zoé", "Alice", "Anaïs", "Marine", "Laura", "Pauline",
    "Mohamed", "Karim", "Amine", "Youssef", "Adam", "Sofiane", "Rayan",
    "Yasmine", "Fatima", "Nour", "Sonia", "Imane", "Dounia", "Myriam",
    "Kevin", "Dylan", "Julien", "Nicolas", "Pierre", "Thomas", "Valentin",
    "Charlotte", "Mathilde", "Océane", "Audrey", "Céline", "Julie", "Claire",
]

def prenom() -> str:
    return random.choice(PRENOMS)