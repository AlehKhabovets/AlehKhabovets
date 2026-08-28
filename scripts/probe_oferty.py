#!/usr/bin/env python3
"""One-off probe: check the oferty.xhtml landing page for links, and try residential-sounding page names."""
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

BASE = "https://mapa.um.warszawa.pl/mapaApp1/faces/oferty"

r = requests.get(BASE + "/oferty.xhtml?lang=pl", headers=HEADERS, timeout=20)
print(f"landing page -> {r.status_code}, {len(r.text)} bytes", file=sys.stderr)
print(r.text, file=sys.stderr)

hrefs = re.findall(r'href="([^"]+)"', r.text)
print(f"hrefs: {hrefs}", file=sys.stderr)

CANDIDATES = [
    "/ofertyMieszkania.xhtml",
    "/ofertyLokaleMieszkalne.xhtml",
    "/lokaleMieszkalne.xhtml",
    "/ofertyMieszkalne.xhtml",
    "/mieszkania.xhtml",
]
for path in CANDIDATES:
    url = BASE + path + "?lang=pl"
    try:
        rr = requests.get(url, headers=HEADERS, timeout=20)
        print(f"{url} -> {rr.status_code}, {len(rr.text)} bytes", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"{url} -> ERROR {exc}", file=sys.stderr)

# also check full ofertyWynajem for 'mieszkal' mentions anywhere (in case it's mixed)
rw = requests.get(BASE + "/ofertyWynajem.xhtml?lang=pl", headers=HEADERS, timeout=20)
print(f"ofertyWynajem contains 'mieszkal': {'mieszkal' in rw.text.lower()}", file=sys.stderr)
