# -*- coding: utf-8 -*-
"""
template_base.py — Classe de base commune à tous les templates.

Chaque template hérite de BaseTemplate et doit définir :
    KEY    : str        → identifiant unique ("NIKE", "AMAZON", …)
    LABEL  : str        → nom affiché dans le bot ("Nike", "Amazon", …)
    FIELDS : list[dict] → champs du formulaire Discord
                          [{"id": "nom", "label": "Nom", "placeholder": "…"}, …]

Et doit implémenter :
    async def generate(self, fields: dict, is_free: bool) -> str
        → retourne le chemin absolu de l'image générée

Les helpers disponibles (self.xxx) évitent la répétition entre templates.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── Chemins globaux ───────────────────────────────────────────────────────────

ROOT   = Path(__file__).parent
ASSETS = ROOT / "assets"
FONTS  = ASSETS / "fonts"
OUTPUT = ROOT / "final"
OUTPUT.mkdir(parents=True, exist_ok=True)


# ── Classe de base ────────────────────────────────────────────────────────────

class BaseTemplate(ABC):

    KEY:    str       = ""
    LABEL:  str       = ""
    FIELDS: list[dict] = []

    # ── Abstract ──────────────────────────────────────────────────────────────

    @abstractmethod
    async def generate(self, fields: dict, is_free: bool) -> str:
        """
        Génère l'image à partir des champs remplis par l'utilisateur.
        Retourne le chemin absolu du fichier PNG produit.
        """
        ...

    # ── Helpers image ─────────────────────────────────────────────────────────

    def new_image(self, size: tuple[int, int], color: str | tuple = "white") -> Image.Image:
        """Crée une nouvelle image RGB vierge."""
        return Image.new("RGB", size, color)

    def new_image_rgba(self, size: tuple[int, int], color: str | tuple = (255, 255, 255, 255)) -> Image.Image:
        """Crée une nouvelle image RGBA (utile pour les overlays transparents)."""
        return Image.new("RGBA", size, color)

    def open_template(self, filename: str) -> Image.Image:
        """Ouvre une image depuis assets/templates/."""
        return Image.open(ASSETS / "templates" / filename).convert("RGBA")

    def open_logo(self, filename: str) -> Image.Image:
        """Ouvre un logo depuis assets/logos/."""
        return Image.open(ASSETS / "logos" / filename).convert("RGBA")

    # ── Helpers police ────────────────────────────────────────────────────────

    def font(self, filename: str, size: int) -> ImageFont.FreeTypeFont:
        """Charge une police depuis assets/fonts/."""
        return ImageFont.truetype(str(FONTS / filename), size)

    def font_calibri(self, size: int) -> ImageFont.FreeTypeFont:
        return self.font("calibri.ttf", size)

    def font_calibri_bold(self, size: int) -> ImageFont.FreeTypeFont:
        return self.font("calibrib.ttf", size)

    def font_calibri_light(self, size: int) -> ImageFont.FreeTypeFont:
        return self.font("calibril.ttf", size)

    # ── Helpers texte ─────────────────────────────────────────────────────────

    def draw_text(
        self,
        draw: ImageDraw.ImageDraw,
        pos: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        fill: str | tuple = "black",
        anchor: str = "la",
    ) -> None:
        """Raccourci pour draw.text avec anchor par défaut."""
        draw.text(pos, text, font=font, fill=fill, anchor=anchor)

    def draw_text_centered(
        self,
        draw: ImageDraw.ImageDraw,
        y: int,
        text: str,
        font: ImageFont.FreeTypeFont,
        fill: str | tuple,
        image_width: int,
    ) -> None:
        """Écrit du texte centré horizontalement sur la largeur de l'image."""
        draw.text((image_width // 2, y), text, font=font, fill=fill, anchor="mt")

    def text_width(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
        """Retourne la largeur en pixels d'un texte."""
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    def text_height(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
        """Retourne la hauteur en pixels d'un texte."""
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[3] - bbox[1]

    # ── Helpers mise en page ──────────────────────────────────────────────────

    def draw_line(
        self,
        draw: ImageDraw.ImageDraw,
        x1: int, y1: int, x2: int, y2: int,
        fill: str | tuple = "#cccccc",
        width: int = 1,
    ) -> None:
        draw.line([(x1, y1), (x2, y2)], fill=fill, width=width)

    def draw_rect(
        self,
        draw: ImageDraw.ImageDraw,
        x1: int, y1: int, x2: int, y2: int,
        fill: str | tuple | None = None,
        outline: str | tuple | None = None,
        width: int = 1,
    ) -> None:
        draw.rectangle([(x1, y1), (x2, y2)], fill=fill, outline=outline, width=width)

    def paste_image(
        self,
        base: Image.Image,
        overlay: Image.Image,
        pos: tuple[int, int],
        resize: tuple[int, int] | None = None,
    ) -> None:
        """
        Colle une image (avec canal alpha si disponible) sur la base.
        pos = (x, y) du coin supérieur gauche.
        """
        if resize:
            overlay = overlay.resize(resize, Image.LANCZOS)
        if overlay.mode == "RGBA":
            base.paste(overlay, pos, overlay)
        else:
            base.paste(overlay, pos)

    # ── Watermark ─────────────────────────────────────────────────────────────

    def add_watermark(
        self,
        img: Image.Image,
        text: str = "FAK-RO",
        opacity: int = 60,          # 0-255
        color: tuple = (200, 200, 200),
        font_size: int = 48,
        angle: int = -30,
        step: int = 200,
    ) -> Image.Image:
        """
        Ajoute un filigrane en diagonale répété sur toute l'image.
        Fonctionne sur les images RGB et RGBA.
        """
        was_rgb = img.mode == "RGB"
        img = img.convert("RGBA")

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)

        try:
            wm_font = self.font_calibri(font_size)
        except Exception:
            wm_font = ImageFont.load_default()

        fill = (*color, opacity)

        w, h = img.size
        for y in range(-h, h * 2, step):
            for x in range(-w, w * 2, step):
                draw.text((x, y), text, font=wm_font, fill=fill)

        from PIL import ImageChops
        import math
        overlay = overlay.rotate(angle, expand=False)

        img = Image.alpha_composite(img, overlay)

        if was_rgb:
            img = img.convert("RGB")
        return img

    # ── Sauvegarde ────────────────────────────────────────────────────────────

    def save(self, img: Image.Image, fmt: str = "PNG") -> str:
        """Sauvegarde l'image dans final/ avec un nom unique. Retourne le path."""
        if img.mode == "RGBA" and fmt == "PNG":
            pass  # PNG supporte RGBA
        elif img.mode == "RGBA":
            img = img.convert("RGB")

        path = OUTPUT / f"{self.KEY}_{uuid.uuid4().hex[:8]}.png"
        img.save(str(path), fmt)
        return str(path)