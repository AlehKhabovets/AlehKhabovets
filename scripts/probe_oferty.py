#!/usr/bin/env python3
"""One-off probe: check the ofertySprzedaz.xhtml offers page and hunt for a rental (najem) equivalent."""
import sys
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
}

BASE = "https://mapa.um.warszawa.pl/mapaApp1/faces/oferty"

CANDIDATES = [
    "/ofertySprzedaz.xhtml",
    "/ofertyNajem.xhtml",
    "/ofertyNajmu.xhtml",
    "/ofertyWynajem.xhtml",
    "/ofertyWynajmu.xhtml",
    "/oferty.xhtml",
]

for path in CANDIDATES:
    url = BASE + path + "?lang=pl"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        print(f"{url} -> {r.status_code}, {len(r.text)} bytes", file=sys.stderr)
        if r.status_code == 200:
            text = r.text
            print(f"  contains 'najem/wynaj': {'najem' in text.lower() or 'wynaj' in text.lower()}", file=sys.stderr)
            print(f"  contains 'sprzedaz': {'sprzeda' in text.lower()}", file=sys.stderr)
            print(f"  contains table/dataTable: {'datatable' in text.lower() or '<table' in text.lower()}", file=sys.stderr)
            print(f"  snippet: {text[:1000]}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"{url} -> ERROR {exc}", file=sys.stderr)
