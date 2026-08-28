#!/usr/bin/env python3
"""One-off probe: find the backend data endpoint behind mapa.um.warszawa.pl's nieruchomosci layer."""
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

resp = requests.get(f"{BASE}/mapaApp1/mapa?service=nieruchomosci", headers=HEADERS, timeout=20)
print(f"config page -> {resp.status_code}, {len(resp.text)} bytes", file=sys.stderr)
full_text = resp.text

# find script src references
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', full_text)
print(f"script refs: {scripts}", file=sys.stderr)

for s in scripts:
    url = s if s.startswith("http") else BASE + (s if s.startswith("/") else "/" + s)
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        print(f"  JS {url} -> {r.status_code}, {len(r.text)} bytes", file=sys.stderr)
        # look for endpoint-like strings
        hits = re.findall(r'["\'](/[A-Za-z0-9_./?=&%-]{5,80})["\']', r.text)
        interesting = [h for h in hits if any(k in h.lower() for k in ["serwer", "servlet", "wfs", "wms", "getfeature", "dane", "api", "json", "nieruch"])]
        if interesting:
            print(f"    interesting paths: {sorted(set(interesting))[:30]}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"  JS {url} -> ERROR {exc}", file=sys.stderr)

# also grep the config page itself for endpoint hints
hits2 = re.findall(r'["\'](/[A-Za-z0-9_./?=&%-]{5,80})["\']', full_text)
interesting2 = [h for h in hits2 if any(k in h.lower() for k in ["serwer", "servlet", "wfs", "wms", "getfeature", "dane", "api", "json"])]
print(f"config-page interesting paths: {sorted(set(interesting2))[:30]}", file=sys.stderr)
