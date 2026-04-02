# -*- coding: utf-8 -*-
"""
templates/__init__.py — Registre auto-découvert des templates.

Au démarrage, ce module scanne tous les fichiers .py du dossier templates/,
importe chaque classe qui hérite de BaseTemplate et a un KEY non vide,
et l'enregistre dans _registry.

Résultat : ajouter un template = créer un fichier. C'est tout.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from pathlib import Path

logger = logging.getLogger(__name__)

# Import différé pour éviter les imports circulaires
# (template_base importe Path etc., pas de dépendance sur templates/)
from template_base import BaseTemplate

_registry: dict[str, BaseTemplate] = {}


def _discover() -> None:
    """Charge tous les modules du dossier templates/ et enregistre les templates."""
    package_dir = Path(__file__).parent

    for finder, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        full_name = f"templates.{module_name}"
        try:
            mod = importlib.import_module(full_name)
        except Exception as e:
            logger.error(f"[TEMPLATES] Erreur import {full_name} : {e}", exc_info=True)
            continue

        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseTemplate)
                and attr is not BaseTemplate
                and attr.KEY  # exclut les classes de base vides
            ):
                instance = attr()
                _registry[instance.KEY] = instance
                logger.info(f"[TEMPLATES] ✅ Chargé : {instance.KEY} → {full_name}.{attr_name}")


_discover()


# ── API publique ──────────────────────────────────────────────────────────────

def get(key: str) -> BaseTemplate:
    """
    Retourne l'instance du template pour la clé donnée.
    Lève KeyError si le template n'existe pas.
    """
    return _registry[key]


def all_templates() -> dict[str, dict]:
    """
    Retourne le dict de config attendu par bot.py :
    { "NIKE": {"label": "Nike", "fields": [...]}, ... }
    """
    return {
        key: {"label": tmpl.LABEL, "fields": tmpl.FIELDS}
        for key, tmpl in sorted(_registry.items())
    }


def keys() -> list[str]:
    """Retourne la liste des clés enregistrées."""
    return list(_registry.keys())