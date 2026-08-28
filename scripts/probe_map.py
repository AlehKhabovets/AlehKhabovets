#!/usr/bin/env python3
"""One-off probe: parse the real homepage HTML for JS bundles, then grep those for API endpoints."""
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

r = requests.get(BASE + "/", headers=HEADERS, timeout=20)
print(f"homepage -> {r.status_code}, {len(r.text)} bytes", file=sys.stderr)
text = r.text

scripts = re.findall(r'<script[^>]*src="([^"]+)"', text)
print(f"script srcs: {scripts}", file=sys.stderr)

links = re.findall(r'href="([^"]*nieruchom[^"]*)"', text, re.IGNORECASE)
print(f"nieruchomosci-related links: {links}", file=sys.stderr)

# also print any onclick / data attrs mentioning nieruchomosci
mentions = re.findall(r'.{80}nieruchom.{80}', text, re.IGNORECASE)
print(f"context around 'nieruchom' mentions ({len(mentions)}):", file=sys.stderr)
for m in mentions[:10]:
    print(f"  ...{m}...", file=sys.stderr)

for s in scripts:
    if s.startswith("http") and "googletagmanager" in s:
        continue
    url = s if s.startswith("http") else BASE + (s if s.startswith("/") else "/" + s)
    try:
        rr = requests.get(url, headers=HEADERS, timeout=20)
        print(f"  JS {url} -> {rr.status_code}, {len(rr.text)} bytes", file=sys.stderr)
        hits = re.findall(r'["\'](/[A-Za-z0-9_./?=&%-]{5,100})["\']', rr.text)
        interesting = [h for h in hits if any(k in h.lower() for k in ["serwer", "servlet", "wfs", "wms", "getfeature", "dane", "api", "nieruch", "mapaapp"])]
        if interesting:
            print(f"    interesting: {sorted(set(interesting))[:40]}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"  JS {url} -> ERROR {exc}", file=sys.stderr)
