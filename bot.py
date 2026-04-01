"""
bot.py — Bot Discord refait proprement.

Flux utilisateur :
  1. /facture  →  SelectView  (menu déroulant de tous les templates)
  2. Choix template  →  Modal page 1 (max 5 champs Discord)
  3. Si > 5 champs  →  Modal page 2 automatique
  4. Soumission  →  ajout dans la file + message de confirmation avec position
  5. Worker  →  génération  →  envoi DM avec l'image

Fix multi-page modal :
  Le problème d'origine est que `collected` était stocké dans l'instance
  InvoiceModal, mais Discord ne conserve pas cet objet entre deux modals
  successifs — chaque soumission crée une nouvelle interaction et l'instance
  de la page précédente est perdue.

  Solution : SESSION_STORE (dict en mémoire) avec un UUID court comme clé,
  passé dans le custom_id du modal.
  Format custom_id : "invoice:{template_key}:{page}:{session_id}"
  Exemple         : "invoice:amazon:0:a1b2c3d4e5f6" (~40 chars, limite = 100)
"""

import asyncio
import json
import logging
import os
import time
import uuid
os.environ['PYTHONUTF8'] = '1'
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import discord
from discord import app_commands
from discord.ext import commands

import generator
from queue_manager import GenerationJob, queue

# ── Config ────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TOKEN          = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
MAX_MODAL_FIELDS = 5   # limite Discord

CONFIG_PATH = Path(__file__).parent / "config" / "templates.json"
with open(CONFIG_PATH, encoding="utf-8") as f:
    TEMPLATES: dict = json.load(f)

# ── Session store ─────────────────────────────────────────────────────────────
# dict[session_id, {"collected": dict, "expires_at": float}]
SESSION_STORE: dict = {}
SESSION_TTL = 600  # 10 minutes

def session_create(collected: dict | None = None) -> str:
    """Crée une session et retourne un ID court (12 hex chars)."""
    session_id = uuid.uuid4().hex[:12]
    SESSION_STORE[session_id] = {
        "collected":  collected or {},
        "expires_at": time.monotonic() + SESSION_TTL,
    }
    return session_id

def session_get(session_id: str) -> dict | None:
    """Retourne collected ou None si session expirée/introuvable."""
    entry = SESSION_STORE.get(session_id)
    if not entry:
        return None
    if time.monotonic() > entry["expires_at"]:
        SESSION_STORE.pop(session_id, None)
        return None
    return entry["collected"]

def session_update(session_id: str, new_data: dict) -> bool:
    """Merge new_data dans collected, refresh le TTL."""
    entry = SESSION_STORE.get(session_id)
    if not entry:
        return False
    entry["collected"].update(new_data)
    entry["expires_at"] = time.monotonic() + SESSION_TTL
    return True

def session_delete(session_id: str) -> None:
    SESSION_STORE.pop(session_id, None)

def session_cleanup() -> None:
    """Supprime les sessions expirées."""
    now = time.monotonic()
    expired = [k for k, v in SESSION_STORE.items() if now > v["expires_at"]]
    for k in expired:
        SESSION_STORE.pop(k, None)

# ── Bot setup ─────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ── Helpers ───────────────────────────────────────────────────────────────────

def is_premium(user: discord.Member | discord.User) -> bool:
    if isinstance(user, discord.Member):
        return any(r.name.upper() == "PREMIUM" for r in user.roles)
    return False

def build_embed_confirm(position: int, label: str, is_free: bool) -> discord.Embed:
    tier  = "FREE ⭐" if is_free else "PREMIUM 👑"
    embed = discord.Embed(
        title="✅ Demande enregistrée",
        description=f"Votre facture **{label}** ({tier}) est en file d'attente.",
        color=discord.Color.blurple() if is_free else discord.Color.green(),
    )
    embed.add_field(name="📋 Position", value=f"**#{position}**", inline=True)
    embed.set_footer(text="Vous recevrez l'image en message privé dès que ce sera prêt.")
    return embed

def build_embed_result(label: str, is_free: bool, image_path: str) -> discord.Embed:
    embed = discord.Embed(
        title="✅ Votre facture est prête !",
        description=f"**{label}**",
        color=discord.Color.yellow(),
    )
    if is_free:
        embed.add_field(
            name="⭐ Passer Premium",
            value="Supprimez le filigrane et accédez à tous les générateurs sans limite.",
            inline=False,
        )
    embed.set_image(url=f"attachment://{Path(image_path).name}")
    return embed

# ── Modal dynamique ───────────────────────────────────────────────────────────

def make_modal(template_key: str, page: int, session_id: str) -> "InvoiceModal":
    """Crée un Modal Discord pour la page donnée du template."""
    cfg         = TEMPLATES[template_key]
    fields      = cfg["fields"]
    start       = page * MAX_MODAL_FIELDS
    end         = min(start + MAX_MODAL_FIELDS, len(fields))
    page_fields = fields[start:end]
    total_pages = (len(fields) - 1) // MAX_MODAL_FIELDS + 1

    title = cfg["label"]
    if total_pages > 1:
        title += f" — Page {page + 1}/{total_pages}"

    return InvoiceModal(
        title        = title,
        template_key = template_key,
        page         = page,
        total_pages  = total_pages,
        page_fields  = page_fields,
        session_id   = session_id,
    )


class InvoiceModal(discord.ui.Modal):
    def __init__(
        self,
        title: str,
        template_key: str,
        page: int,
        total_pages: int,
        page_fields: list,
        session_id: str,
    ):
        # custom_id format : "invoice:{template_key}:{page}:{session_id}"
        # ex : "invoice:amazon:0:a1b2c3d4e5f6"  ≈ 38 chars ✅ (limite Discord = 100)
        custom_id = f"invoice:{template_key}:{page}:{session_id}"
        super().__init__(title=title, custom_id=custom_id, timeout=300)

        self.template_key = template_key
        self.page         = page
        self.total_pages  = total_pages
        self.session_id   = session_id

        # Ajout dynamique des champs TextInput
        self._field_ids: list[str] = []
        for field_cfg in page_fields:
            ti = discord.ui.TextInput(
                label       = field_cfg["label"],
                placeholder = field_cfg.get("placeholder", ""),
                required    = True,
                max_length  = 200,
                style       = discord.TextStyle.short,
            )
            self.add_item(ti)
            self._field_ids.append(field_cfg["id"])

    async def on_submit(self, interaction: discord.Interaction):
        # Sauvegarde les valeurs de cette page dans la session
        new_data = {
            field_id: text_input.value  # type: ignore[union-attr]
            for field_id, text_input in zip(self._field_ids, self.children)
        }
        if not session_update(self.session_id, new_data):
            await interaction.response.send_message(
                "❌ Session expirée (10 min). Relancez `/facture`.", ephemeral=True
            )
            return

        next_page = self.page + 1
        if next_page < self.total_pages:
            # Il reste des pages → ouvrir le modal suivant (même session_id)
            next_modal = make_modal(self.template_key, next_page, self.session_id)
            await interaction.response.send_modal(next_modal)
        else:
            # Toutes les pages remplies → enqueue
            collected = dict(session_get(self.session_id) or {})
            session_delete(self.session_id)
            await _enqueue_job(interaction, self.template_key, collected)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        logger.error(f"Erreur modal : {error}", exc_info=True)
        await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

# ── Enqueue helper ────────────────────────────────────────────────────────────

async def _enqueue_job(interaction: discord.Interaction, template_key: str, fields: dict):
    cfg     = TEMPLATES[template_key]
    user    = interaction.user
    is_free = not is_premium(user)

    async def on_done(path: str):
        embed = build_embed_result(cfg["label"], is_free, path)
        try:
            await user.send(embed=embed, file=discord.File(path))
        except discord.Forbidden:
            logger.warning(f"Impossible d'envoyer le DM à {user}")
        try:
            os.remove(path)
        except OSError:
            pass
        if LOG_CHANNEL_ID and not is_free:
            ch = bot.get_channel(LOG_CHANNEL_ID)
            if ch:
                log_embed = discord.Embed(
                    title="👑 PREMIUM — Génération",
                    description=f"**{user}** a généré une facture **{cfg['label']}**",
                    color=discord.Color.gold(),
                )
                await ch.send(embed=log_embed)

    job = GenerationJob(
        user           = user,
        template_key   = template_key,
        template_label = cfg["label"],
        fields         = fields,
        is_free        = is_free,
        interaction    = interaction,
        on_done        = on_done,
    )
    position = await queue.enqueue(job)

    embed = build_embed_confirm(position, cfg["label"], is_free)
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.InteractionResponded:
        await interaction.followup.send(embed=embed, ephemeral=True)

# ── Sélecteur de template ─────────────────────────────────────────────────────

class TemplateSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=cfg["label"], value=key)
            for key, cfg in TEMPLATES.items()
        ]
        super().__init__(
            placeholder="Choisissez un template de facture…",
            min_values=1,
            max_values=1,
            options=options[:25],
        )

    async def callback(self, interaction: discord.Interaction):
        template_key = self.values[0]
        session_id   = session_create()          # ← nouvelle session vide
        modal        = make_modal(template_key, page=0, session_id=session_id)
        await interaction.response.send_modal(modal)

class TemplateSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TemplateSelect())

# ── Commandes slash ───────────────────────────────────────────────────────────

@tree.command(name="facture", description="Générer une facture de marque")
async def cmd_facture(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🧾 Générateur de Factures",
        description="Sélectionnez le template de votre choix ci-dessous.",
        color=discord.Color.blurple(),
    )
    view = TemplateSelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@tree.command(name="queue", description="Voir la taille de la file d'attente")
async def cmd_queue(interaction: discord.Interaction):
    size = queue.size()
    embed = discord.Embed(
        title="📋 File d'attente",
        description=f"**{size}** génération(s) en attente.",
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ── Événements bot ────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    logger.info(f"✅ Connecté en tant que {bot.user} (id={bot.user.id})")
    try:
        synced = await tree.sync()
        logger.info(f"✅ {len(synced)} commande(s) synchronisée(s)")
    except Exception as e:
        logger.error(f"Erreur sync commandes : {e}")

    asyncio.create_task(queue.start_worker(generator.generate))
    asyncio.create_task(_session_cleanup_loop())
    logger.info("✅ Worker de génération démarré")

async def _session_cleanup_loop():
    """Nettoie les sessions expirées toutes les 60 secondes."""
    while True:
        await asyncio.sleep(60)
        session_cleanup()

# ── Point d'entrée ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(TOKEN)