#!/usr/bin/env python3
"""One-off probe: inspect Otodom's embedded __NEXT_DATA__ JSON to locate the listings array."""
import json
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

URL = (
    "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"
    "?priceMax=2500&limit=36"
)

resp = requests.get(URL, headers=HEADERS, timeout=30)
print(f"HTTP {resp.status_code}, {len(resp.text)} bytes", file=sys.stderr)

m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
if not m:
    print("__NEXT_DATA__ not found", file=sys.stderr)
    sys.exit(0)

data = json.loads(m.group(1))
print(f"top-level keys: {list(data.keys())}", file=sys.stderr)

props = data.get("props", {}).get("pageProps", {})
print(f"pageProps keys: {list(props.keys())}", file=sys.stderr)

# Hunt for the array of listings anywhere in pageProps
def walk(node, path="", depth=0):
    if depth > 6:
        return
    if isinstance(node, dict):
        if "items" in node and isinstance(node["items"], list) and node["items"]:
            first = node["items"][0]
            if isinstance(first, dict):
                print(f"  ARRAY at {path}.items ({len(node['items'])} items)", file=sys.stderr)
                print(f"    item keys: {list(first.keys())}", file=sys.stderr)
                print(f"    sample: {json.dumps(first, ensure_ascii=False)[:900]}", file=sys.stderr)
        for k, v in node.items():
            walk(v, f"{path}.{k}", depth + 1)
    elif isinstance(node, list) and node and isinstance(node[0], dict):
        keys = set(node[0].keys())
        if {"title", "id"} <= keys or {"slug"} <= keys:
            print(f"  LIST at {path} ({len(node)}) item keys: {list(node[0].keys())}", file=sys.stderr)

walk(props, "pageProps")
