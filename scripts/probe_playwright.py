#!/usr/bin/env python3
"""One-off probe: check if a real headless browser gets past the WAF on gov sites."""
import sys
from playwright.sync_api import sync_playwright

URLS = [
    "https://mieszkania.um.warszawa.pl/",
    "https://wola.um.warszawa.pl/waw/zgn-wola/lokale-mieszkalne",
    "https://bip.warszawa.pl/",
]

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
    for url in URLS:
        try:
            resp = page.goto(url, timeout=30000, wait_until="domcontentloaded")
            status = resp.status if resp else None
            content = page.content()
            print(f"{url} -> HTTP {status}, length {len(content)}", file=sys.stderr)
            if status and status < 400:
                snippet = content[:300].replace("\n", " ")
                print(f"  snippet: {snippet}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            print(f"{url} -> ERROR: {exc}", file=sys.stderr)
    browser.close()
