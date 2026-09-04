#!/usr/bin/env python3
"""One-off probe: which Polish rental portals are reachable from GitHub Actions
for the original search — Warsaw apartments for rent, up to 2500 PLN/month."""
import re
import sys

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

PORTALS = {
    "otodom": "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa?priceMax=2500",
    "gratka": "https://gratka.pl/nieruchomosci/mieszkania/warszawa/wynajem?cena-do=2500",
    "morizon": "https://www.morizon.pl/do-wynajecia/mieszkania/warszawa/?ps%5Bprice_to%5D=2500",
    "domiporta": "https://www.domiporta.pl/mieszkanie/wynajme/mazowieckie/warszawa?Price.To=2500",
    "nieruchomosci-online": "https://warszawa.nieruchomosci-online.pl/szukaj.html?3,mieszkanie,wynajem,,Warszawa,,,,,,,,,,,,,2500",
    "olx (dla porównania)": "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/warszawa/?search%5Bfilter_float_price:to%5D=2500",
}

for name, url in PORTALS.items():
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        text = resp.text
        print(f"=== {name} -> HTTP {resp.status_code}, {len(text)} bytes ===", file=sys.stderr)
        if resp.status_code == 200:
            # crude signal that real listings are present: count PLN price mentions
            prices = re.findall(r"\d[\d\s ]{2,6}\s*zł", text)
            print(f"    price-like matches: {len(prices)}; sample: {prices[:8]}", file=sys.stderr)
            print(f"    mentions 'wynaj': {text.lower().count('wynaj')}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"=== {name} -> ERROR: {exc}", file=sys.stderr)
