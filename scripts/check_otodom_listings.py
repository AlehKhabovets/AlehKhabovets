#!/usr/bin/env python3
"""Check Otodom for new Warsaw flat rentals under a price cap and notify via Telegram.

Replaces the OLX source, which started returning 403 to automated requests.
Otodom embeds its search results as JSON in __NEXT_DATA__, so we read that
instead of scraping markup.
"""
import json
import os
import re
import sys
from pathlib import Path

import requests

from telegram_utils import send_digest

PRICE_MAX = int(os.environ.get("PRICE_MAX_PLN", "2500"))
SEARCH_URL = (
    "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"
    f"?priceMax={PRICE_MAX}&limit=36&by=LATEST&direction=DESC"
)
STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_otodom.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def load_seen() -> set:
    if STATE_PATH.exists():
        return set(json.loads(STATE_PATH.read_text()))
    return set()


def save_seen(seen: set) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2))


def extract_price(raw) -> int | None:
    """totalPrice comes as {'value': 2500, 'currency': 'PLN'} but tolerate other shapes."""
    if isinstance(raw, dict):
        raw = raw.get("value")
    if isinstance(raw, (int, float)):
        return int(raw)
    if isinstance(raw, str):
        digits = re.sub(r"[^\d]", "", raw)
        return int(digits) if digits else None
    return None


def build_url(item: dict) -> str:
    href = item.get("href")
    if href:
        return href if href.startswith("http") else "https://www.otodom.pl" + href
    slug = item.get("slug")
    return f"https://www.otodom.pl/pl/oferta/{slug}" if slug else "https://www.otodom.pl/"


def describe_location(item: dict) -> str:
    address = (item.get("location") or {}).get("address") or {}
    parts = []
    street = (address.get("street") or {}).get("name")
    city = (address.get("city") or {}).get("name")
    if street:
        parts.append(street)
    if city:
        parts.append(city)
    return ", ".join(parts)


def fetch_listings():
    resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=30)
    print(f"Otodom response status: {resp.status_code}, length: {len(resp.text)}", file=sys.stderr)
    resp.raise_for_status()

    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
    if not match:
        print("__NEXT_DATA__ block not found — page layout may have changed", file=sys.stderr)
        return []

    data = json.loads(match.group(1))
    items = (
        data.get("props", {})
        .get("pageProps", {})
        .get("data", {})
        .get("searchAds", {})
        .get("items", [])
    )
    print(f"Found {len(items)} items in search results", file=sys.stderr)

    listings = []
    for item in items:
        item_id = item.get("id")
        if item_id is None:
            continue
        price = extract_price(item.get("totalPrice"))
        if price is not None and price > PRICE_MAX:
            continue

        listings.append(
            {
                "id": str(item_id),
                "title": item.get("title") or "Без названия",
                "price": price,
                "area": item.get("areaInSquareMeters"),
                "rooms": item.get("roomsNumber"),
                "location": describe_location(item),
                "private_owner": bool(item.get("isPrivateOwner")),
                "url": build_url(item),
            }
        )
    return listings


def format_listing(item: dict) -> str:
    price = f"{item['price']} zł/мес" if item["price"] is not None else "цена не указана"
    details = [price]
    if item["area"]:
        details.append(f"{item['area']} м²")
    if item["rooms"]:
        details.append(f"{item['rooms']} комн.")
    if item["private_owner"]:
        details.append("от собственника")

    lines = [f"<b>{item['title']}</b>", " · ".join(details)]
    if item["location"]:
        lines.append(item["location"])
    lines.append(item["url"])
    return "\n".join(lines)


def main() -> None:
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    seen = load_seen()
    try:
        listings = fetch_listings()
    except (requests.RequestException, json.JSONDecodeError) as exc:
        print(f"Failed to fetch Otodom: {exc}", file=sys.stderr)
        sys.exit(1)

    new_listings = [item for item in listings if item["id"] not in seen]
    print(f"{len(listings)} within budget, {len(new_listings)} new", file=sys.stderr)

    if dry_run:
        print("DRY_RUN=true, skipping Telegram send and state update", file=sys.stderr)
        for item in listings[:10]:
            print(format_listing(item), file=sys.stderr)
            print("---", file=sys.stderr)
        return

    if new_listings:
        header = f"🏠 Новые квартиры в аренду (Варшава, до {PRICE_MAX} zł): {len(new_listings)}"
        send_digest(header, [format_listing(item) for item in new_listings])
    else:
        print("No new listings, nothing to send", file=sys.stderr)

    seen.update(item["id"] for item in listings)
    save_seen(seen)


if __name__ == "__main__":
    main()
