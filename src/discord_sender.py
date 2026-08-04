"""Envia o digest final para um canal do Discord via webhook."""
from __future__ import annotations

import requests

DISCORD_LIMIT = 1900  # margem de seguranca abaixo do limite de 2000 chars do Discord


def send_to_discord(webhook_url: str, content: str, title: str = "Radar de Tecnologia") -> None:
    header = f"**{title}**\n\n"
    chunks = _chunk(header + content, DISCORD_LIMIT)
    for chunk in chunks:
        r = requests.post(webhook_url, json={"content": chunk}, timeout=15)
        r.raise_for_status()


def _chunk(text: str, size: int) -> list[str]:
    lines = text.split("\n")
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > size:
            chunks.append(current)
            current = ""
        current += line + "\n"
    if current:
        chunks.append(current)
    return chunks
