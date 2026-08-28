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
    "https://warszawa19115.pl/en/-/lokal-za-remont",
    "https://listaprzetargow.pl/oferty/warszawa",
    "https://www.oferent.com.pl/przetargi/warszawa/",
    "https://przetargi.adradar.pl/p/mieszkania/55060/Warszawa/a",
    "https://e-przetargi.pl/zamowienia-publiczne/przetarg/1406/najem-lokalu-mieszkalnego-w-warszawie",
    "https://www.przetargi.egospodarka.pl/",
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
