#!/usr/bin/env python3
"""One-off probe: fully parse the nieruchomosci config XML for server/service/URL tags."""
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

r = requests.get(BASE + "/mapaApp1/mapa?service=nieruchomosci", headers=HEADERS, timeout=20)
text = r.text
print(f"config -> {r.status_code}, {len(text)} bytes", file=sys.stderr)

# find all XML tags whose name suggests a server/service/url/layer definition
tag_hits = re.findall(r"<([A-Za-z_]*(?:erver|ervice|rl|ayer|WMS|WFS|Feature)[A-Za-z_]*)>([^<]{0,150})</\1>", text)
print(f"server/service/url/layer-ish tags ({len(tag_hits)}):", file=sys.stderr)
for name, val in tag_hits[:60]:
    print(f"  <{name}> = {val}", file=sys.stderr)

# find any http(s):// URLs embedded anywhere in the XML
urls = re.findall(r'https?://[^\s"<>]+', text)
print(f"embedded absolute URLs ({len(urls)}):", file=sys.stderr)
for u in sorted(set(urls))[:40]:
    print(f"  {u}", file=sys.stderr)

# find any .aspx/.ashx/.do/.jsp/servlet-like tokens
endpointish = re.findall(r'[A-Za-z0-9_./-]+\.(?:aspx|ashx|do|jsp|cgi)\b', text)
print(f"endpoint-like tokens: {sorted(set(endpointish))[:40]}", file=sys.stderr)
