# -*- coding: utf-8 -*-
"""
generator.py -- Dispatcher.
Appelle le bon fichier generators/xxx.py selon la cle du template.
"""
import importlib

# Mapping cle template -> module
MODULES = {
    "NIKE":           "generators.nike",
    "LOUIS_VUITTON_1":"generators.louis_vuitton",
    "BURBERRY":       "generators.burberry",
    "GUCCI":          "generators.gucci",
    "STUSSY":         "generators.stussy",
    "PRADA":          "generators.prada",
    "SUPREME":        "generators.supreme",
    "TST":            "generators.stone_island",
    "WTH":            "generators.wethenew",
    "JACQUEMUS":      "generators.jacquemus",
    "AMAZON":         "generators.amazon",
    "FENDI":          "generators.fendi",
    "CORTEIZ":        "generators.corteiz",
    "FARFETCH":       "generators.farfetch",
    "AMI":            "generators.ami",
    "GOYARD":         "generators.goyard",
    "LACOSTE":        "generators.lacoste",
    "ZALANDO":        "generators.zalando",
    "DIOR":           "generators.dior",
    "STOCKX":         "generators.stockx",
    "TRAPSTAR":       "generators.trapstar",
    "SYNAWORLD":      "generators.synaworld",
    "APPLE": "generators.apple",
}

async def generate(template_key, fields, is_free):
    module_name = MODULES[template_key]
    mod = importlib.import_module(module_name)
    return await mod.generate(fields, is_free)