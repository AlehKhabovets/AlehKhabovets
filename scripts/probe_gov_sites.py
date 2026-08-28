#!/usr/bin/env python3
"""One-off probe: check reachability and structure of Warsaw municipal housing sites."""
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
    "https://mieszkania.um.warszawa.pl/",
    "https://mieszkania.um.warszawa.pl/chcesz-wynajac-lokal",
    "https://um.warszawa.pl/-/domy-komunalne",
    "https://wola.um.warszawa.pl/waw/zgn-wola/lokale-mieszkalne",
    "https://warszawa19115.pl/en/-/najem-komunalnego-lokalu-uzytkowego-w-przetargu",
    "https://srodmiescie.um.warszawa.pl/waw/zgn-srodmiescie/zamowienie",
]

for url in URLS:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        print(f"{url} -> HTTP {resp.status_code}, length {len(resp.text)}", file=sys.stderr)
        if resp.status_code == 200:
            snippet = resp.text[:300].replace("\n", " ")
            print(f"  snippet: {snippet}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"{url} -> ERROR: {exc}", file=sys.stderr)
