#!/usr/bin/env python3
"""One-off probe: check the real mapa.um.warszawa.pl app page and tech stack for the nieruchomosci layer."""
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

BASE = "https://mapa.um.warszawa.pl"

CANDIDATES = [
    "/mapaApp1/",
    "/mapaApp1/index.html",
    "/mapaApp1/mapa",
    "/mapaApp1/mapa.html",
]

for path in CANDIDATES:
    url = BASE + path
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        print(f"{url} -> {r.status_code}, {len(r.text)} bytes", file=sys.stderr)
        if r.status_code == 200:
            text = r.text
            has_swf = ".swf" in text.lower()
            print(f"  contains .swf reference: {has_swf}", file=sys.stderr)
            scripts = re.findall(r'src="([^"]+)"', text)
            print(f"  src refs: {scripts[:20]}", file=sys.stderr)
            print(f"  snippet: {text[:600]}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"{url} -> ERROR {exc}", file=sys.stderr)
