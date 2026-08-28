#!/usr/bin/env python3
"""One-off probe: check reachability of Warsaw's real-estate map service and hunt for its backend API."""
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
    "https://mapa.um.warszawa.pl/mapaApp1/mapa?service=nieruchomosci",
    "https://mapa.um.warszawa.pl/",
]

for url in URLS:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        print(f"{url} -> HTTP {resp.status_code}, length {len(resp.text)}", file=sys.stderr)
        if resp.status_code == 200:
            text = resp.text
            snippet = text[:1500].replace("\n", " ")
            print(f"  snippet: {snippet}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"{url} -> ERROR: {exc}", file=sys.stderr)
