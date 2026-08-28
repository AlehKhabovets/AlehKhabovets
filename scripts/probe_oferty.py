#!/usr/bin/env python3
"""One-off probe: dump the ofertyWynajem.xhtml rental offers table structure."""
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

# find the data table region
m = re.search(r'<table[^>]*>.*?</table>', text, re.DOTALL)
if m:
    table_html = m.group(0)
    print(f"table length: {len(table_html)}", file=sys.stderr)
    print(table_html[:6000], file=sys.stderr)
else:
    print("no <table> found via regex, searching for ui-datatable div", file=sys.stderr)
    m2 = re.search(r'<div[^>]*ui-datatable[^>]*>.*', text, re.DOTALL)
    if m2:
        print(m2.group(0)[:6000], file=sys.stderr)
    else:
        print("dumping full body instead:", file=sys.stderr)
        body = re.search(r'<body.*</body>', text, re.DOTALL)
        print((body.group(0) if body else text)[:6000], file=sys.stderr)

# row count hints
rows = re.findall(r'<tr[^>]*>', text)
print(f"approx <tr> count: {len(rows)}", file=sys.stderr)

# look for pagination / ajax hints
print(f"contains 'ui-paginator': {'ui-paginator' in text}", file=sys.stderr)
print(f"contains 'PrimeFaces.ajax': {'PrimeFaces.ajax' in text}", file=sys.stderr)
