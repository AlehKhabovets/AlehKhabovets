#!/usr/bin/env python3
"""One-off probe: capture all network requests a real browser makes when loading the nieruchomosci map."""
import sys
from playwright.sync_api import sync_playwright

URL = "https://mapa.um.warszawa.pl/mapaApp1/mapa?service=nieruchomosci"
STATIC_EXT = (".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".ico")

requests_seen = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="pl-PL",
    )
    page = context.new_page()
    page.on("request", lambda req: requests_seen.append((req.method, req.url)))

    try:
        page.goto(URL, timeout=30000, wait_until="load")
        page.wait_for_timeout(5000)
    except Exception as exc:  # noqa: BLE001
        print(f"navigation error: {exc}", file=sys.stderr)

    print(f"total requests captured: {len(requests_seen)}", file=sys.stderr)
    print("=== all requests ===", file=sys.stderr)
    for method, url in requests_seen:
        print(f"  {method} {url}", file=sys.stderr)

    print("=== non-static requests (likely data/API calls) ===", file=sys.stderr)
    for method, url in requests_seen:
        if not url.lower().endswith(STATIC_EXT):
            print(f"  {method} {url}", file=sys.stderr)

    browser.close()
