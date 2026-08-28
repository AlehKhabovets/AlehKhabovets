#!/usr/bin/env python3
"""One-off probe: dump ALL tables and tbody content to find actual data rows."""
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

url = "https://mapa.um.warszawa.pl/mapaApp1/faces/oferty/ofertyWynajem.xhtml?lang=pl"
r = requests.get(url, headers=HEADERS, timeout=20)
text = r.text
print(f"{url} -> {r.status_code}, {len(text)} bytes", file=sys.stderr)

tables = re.findall(r'<table[^>]*>.*?</table>', text, re.DOTALL)
print(f"number of <table> blocks: {len(tables)}", file=sys.stderr)
for i, t in enumerate(tables):
    print(f"--- table {i}, length {len(t)} ---", file=sys.stderr)
    print(t[:2000], file=sys.stderr)

tbodies = re.findall(r'<tbody[^>]*>.*?</tbody>', text, re.DOTALL)
print(f"number of <tbody> blocks: {len(tbodies)}", file=sys.stderr)
for i, tb in enumerate(tbodies):
    print(f"--- tbody {i}, length {len(tb)} ---", file=sys.stderr)
    print(tb[:3000], file=sys.stderr)

print(f"contains 'Brak' (no results marker): {'Brak' in text}", file=sys.stderr)
print(f"contains 'ui-datatable-data': {'ui-datatable-data' in text}", file=sys.stderr)
