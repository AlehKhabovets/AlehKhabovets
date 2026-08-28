#!/usr/bin/env python3
"""One-off probe: check whether tender aggregators cover rentals (najem) vs sales (sprzedaz)."""
import re
import sys
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
}

URLS = [
    "https://listaprzetargow.pl/oferty/warszawa",
    "https://przetargi.adradar.pl/p/mieszkania/55060/Warszawa/a",
]


def count_ci(text: str, word: str) -> int:
    return len(re.findall(word, text, re.IGNORECASE))


for url in URLS:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    text = resp.text
    print(f"=== {url} -> HTTP {resp.status_code} ===", file=sys.stderr)
    print(f"  'najem' count: {count_ci(text, 'najem')}", file=sys.stderr)
    print(f"  'sprzedaż/sprzedaz' count: {count_ci(text, 'sprzeda')}", file=sys.stderr)
    print(f"  'wynajem' count: {count_ci(text, 'wynaj')}", file=sys.stderr)
    print(f"  'remont' count: {count_ci(text, 'remont')}", file=sys.stderr)
    # show a few lines around each 'najem' occurrence for context
    for m in list(re.finditer("najem", text, re.IGNORECASE))[:5]:
        start = max(0, m.start() - 100)
        end = min(len(text), m.end() + 100)
        snippet = re.sub(r"\s+", " ", text[start:end])
        print(f"  ...{snippet}...", file=sys.stderr)
