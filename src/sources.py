"""Coleta de conteudo de fontes publicas de tecnologia (sem login, sem automacao de rede social)."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "tech-radar-bot/1.0 (uso pessoal)"}


def fetch_hackernews(min_points: int = 50, limit: int = 8) -> list[dict]:
    """Top stories das ultimas 24h no Hacker News, via Algolia API."""
    url = "https://hn.algolia.com/api/v1/search_by_date"
    params = {
        "tags": "story",
        "numericFilters": f"points>{min_points},created_at_i>{_yesterday_ts()}",
        "hitsPerPage": limit,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    hits = r.json().get("hits", [])
    return [
        {
            "title": h.get("title"),
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
            "points": h.get("points"),
        }
        for h in hits
        if h.get("title")
    ]


def fetch_github_trending(language: str = "", limit: int = 8) -> list[dict]:
    """Repos em alta hoje no GitHub Trending (scraping da pagina publica, sem API oficial)."""
    url = f"https://github.com/trending/{language}".rstrip("/")
    r = requests.get(url, params={"since": "daily"}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    repos = []
    for article in soup.select("article.Box-row")[:limit]:
        h2 = article.select_one("h2 a")
        if not h2:
            continue
        name = h2.get_text(strip=True).replace(" ", "").replace("\n", "")
        href = h2.get("href", "")
        desc_tag = article.select_one("p")
        desc = desc_tag.get_text(strip=True) if desc_tag else ""
        stars_tag = article.select_one('a[href$="/stargazers"]')
        stars = stars_tag.get_text(strip=True) if stars_tag else "?"
        repos.append(
            {
                "name": name,
                "url": f"https://github.com{href}",
                "description": desc,
                "stars_total": stars,
            }
        )
    return repos


def fetch_lobsters(limit: int = 8) -> list[dict]:
    """Posts em alta no Lobsters (comunidade tecnica, API JSON publica sem auth).

    Nota: a API JSON do Reddit hoje exige OAuth mesmo pra leitura (retorna 403
    pra requests sem login) -- por isso o radar usa Lobsters como fonte de
    comunidade no lugar do Reddit.
    """
    url = "https://lobste.rs/hottest.json"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return [
        {
            "title": p.get("title"),
            "url": p.get("url") or p.get("comments_url"),
            "score": p.get("score"),
            "tags": p.get("tags", []),
        }
        for p in r.json()[:limit]
    ]


def fetch_devto(limit: int = 8) -> list[dict]:
    """Artigos em alta no dev.to (API publica oficial)."""
    url = "https://dev.to/api/articles"
    r = requests.get(url, params={"top": 1, "per_page": limit}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return [
        {
            "title": a.get("title"),
            "url": a.get("url"),
            "reactions": a.get("public_reactions_count"),
            "tags": a.get("tag_list", []),
        }
        for a in r.json()
    ]


def _yesterday_ts() -> int:
    import time

    return int(time.time()) - 24 * 3600
