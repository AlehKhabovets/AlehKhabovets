#!/usr/bin/env python3
"""One-off probe: check BIP (Biuletyn Informacji Publicznej) reachability."""
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
    "https://bip.warszawa.pl/",
    "https://warszawa19115.pl/en/-/lokal-za-remont",
    "https://warszawa19115.pl/en/-/najem-lokalu-mieszkalnego-z-zasobu-miasta-",
]

for url in URLS:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        print(f"{url} -> HTTP {resp.status_code}, length {len(resp.text)}", file=sys.stderr)
        if resp.status_code == 200:
            text = resp.text
            for kw in ["adres", "ul.", "m2", "m²", "zł", "przetarg", "ogłoszenie"]:
                print(f"  '{kw}' count: {text.lower().count(kw.lower())}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"{url} -> ERROR: {exc}", file=sys.stderr)
