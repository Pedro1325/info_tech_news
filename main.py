"""Radar diario de tecnologia: coleta HN/GitHub/Reddit/dev.to, gera ideias com Claude
e manda um resumo pro Discord. Pensado pra rodar 1x/dia via Task Scheduler."""
from __future__ import annotations

import logging
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from src import digest, discord_sender, sources

# console do Windows costuma usar cp1252; titulos com acentos/emoji quebrariam o log sem isso
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
DIGEST_DIR = BASE_DIR / "digests"

LOG_DIR.mkdir(exist_ok=True)
DIGEST_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "tech-radar.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("tech-radar")


def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    api_key = os.environ["ANTHROPIC_API_KEY"]
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

    log.info("Coletando fontes...")
    hn = _safe(sources.fetch_hackernews, "Hacker News")
    gh = _safe(sources.fetch_github_trending, "GitHub Trending")
    lobsters = _safe(sources.fetch_lobsters, "Lobsters")
    devto = _safe(sources.fetch_devto, "dev.to")

    raw = digest.build_raw_digest(hn, gh, lobsters, devto)
    if not raw.strip():
        log.warning("Nenhuma fonte retornou conteudo hoje. Abortando.")
        return

    log.info("Gerando resumo e ideias com Claude...")
    result = digest.generate_ideas(raw, api_key)

    today = date.today().isoformat()
    out_file = DIGEST_DIR / f"{today}.md"
    out_file.write_text(f"# Radar de Tecnologia - {today}\n\n{result}\n\n---\n\n## Fontes brutas\n\n{raw}\n", encoding="utf-8")
    log.info("Digest salvo em %s", out_file)

    log.info("Enviando para o Discord...")
    discord_sender.send_to_discord(webhook_url, result, title=f"Radar de Tecnologia - {today}")
    log.info("Concluido.")


def _safe(fn, label: str):
    try:
        return fn()
    except Exception:
        log.exception("Falha ao coletar %s, seguindo sem essa fonte", label)
        return []


if __name__ == "__main__":
    main()
