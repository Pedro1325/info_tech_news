"""Monta o digest bruto do dia e pede pra Claude resumir + sugerir ideias."""
from __future__ import annotations

import anthropic

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = (
    "Voce e um analista de tendencias de tecnologia que ajuda um profissional de TI "
    "a manter presenca ativa no LinkedIn. Dado um apanhado bruto de links e titulos "
    "do dia (Hacker News, GitHub Trending, Lobsters, dev.to), voce escreve em portugues "
    "do Brasil um resumo curto e acionavel, no seguinte formato:\n\n"
    "## Tendencias de hoje\n"
    "- 3 a 5 bullets com os assuntos mais relevantes do dia e por que importam\n\n"
    "## Ideias de projeto\n"
    "- 2 ideias de projeto pessoal inspiradas no que esta em alta, com 1 frase de escopo cada\n\n"
    "## Angulos pra postar no LinkedIn\n"
    "- 2 ganchos de post (hook + argumento em 1-2 frases) conectando as tendencias a "
    "experiencia de um profissional de tecnologia\n\n"
    "Seja direto, sem enrolacao, sem emojis em excesso (no maximo 1 por secao). "
    "Cite as fontes relevantes (nome + link) dentro dos bullets quando fizer sentido."
)


def build_raw_digest(hn: list[dict], gh: list[dict], lobsters: list[dict], devto: list[dict]) -> str:
    parts = []

    if hn:
        parts.append("### Hacker News (24h)")
        parts += [f"- {h['title']} ({h['points']} pts) - {h['url']}" for h in hn]

    if gh:
        parts.append("\n### GitHub Trending (hoje)")
        parts += [
            f"- {r['name']} [{r['stars_total']} estrelas total] - {r['description']} - {r['url']}"
            for r in gh
        ]

    if lobsters:
        parts.append("\n### Lobsters (top do momento)")
        parts += [
            f"- {p['title']} [{', '.join(p['tags'])}] ({p['score']} pts) - {p['url']}"
            for p in lobsters
        ]

    if devto:
        parts.append("\n### dev.to (top do dia)")
        parts += [
            f"- {a['title']} [{', '.join(a['tags'])}] ({a['reactions']} reacoes) - {a['url']}"
            for a in devto
        ]

    return "\n".join(parts)


def generate_ideas(raw_digest: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw_digest}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
