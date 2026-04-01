"""
queue_manager.py — File d'attente async pour les générations d'images.

Une seule génération tourne à la fois (pour éviter la surcharge I/O).
Chaque job est un dict :
  {
    "user"          : discord.User,
    "template_key"  : str,
    "fields"        : dict,
    "is_free"       : bool,
    "interaction"   : discord.Interaction,   # pour le feedback de position
  }
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Callable, Awaitable

import discord

logger = logging.getLogger(__name__)


@dataclass
class GenerationJob:
    user: discord.User
    template_key: str
    template_label: str
    fields: dict
    is_free: bool
    interaction: discord.Interaction
    # Callback appelé quand le job est traité : async def callback(path: str) -> None
    on_done: Callable[[str], Awaitable[None]]


class GenerationQueue:
    def __init__(self):
        self._queue: asyncio.Queue[GenerationJob] = asyncio.Queue()
        self._running = False

    def size(self) -> int:
        return self._queue.qsize()

    async def enqueue(self, job: GenerationJob) -> int:
        """Ajoute un job. Retourne la position dans la file (1-indexed)."""
        await self._queue.put(job)
        pos = self._queue.qsize()
        logger.info(f"[QUEUE] Job ajouté — user={job.user} template={job.template_key} position={pos}")
        return pos

    async def start_worker(self, generator_fn: Callable) -> None:
        """
        Lance la boucle de traitement.
        generator_fn(template_cfg, fields, is_free) -> str (path)
        """
        if self._running:
            return
        self._running = True
        logger.info("[QUEUE] Worker démarré")

        while self._running:
            try:
                job: GenerationJob = await asyncio.wait_for(self._queue.get(), timeout=2.0)
            except asyncio.TimeoutError:
                continue

            logger.info(f"[QUEUE] Traitement — user={job.user} template={job.template_key}")

            try:
                path = await generator_fn(job.template_key, job.fields, job.is_free)
                await job.on_done(path)
            except Exception as e:
                logger.error(f"[QUEUE] Erreur génération : {e}", exc_info=True)
                await _send_error(job.interaction, job.user)
            finally:
                self._queue.task_done()

    def stop(self):
        self._running = False


async def _send_error(interaction: discord.Interaction, user: discord.User):
    embed = discord.Embed(
        title="⛔ Erreur de génération",
        description="Une erreur s'est produite. Vérifiez vos paramètres et réessayez.",
        color=discord.Color.red(),
    )
    try:
        await user.send(embed=embed)
    except discord.Forbidden:
        pass


# Instance globale partagée
queue = GenerationQueue()