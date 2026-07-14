#!/usr/bin/env python3
"""Check OLX for new Warsaw rental listings under a price cap and notify via Telegram."""
import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OLX_URL = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/warszawa/"
PRICE_MAX = int(os.environ.get("PRICE_MAX_PLN", "2500"))
STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_listings.json"

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


def parse_price(raw: str):
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def fetch_listings():
    params = {"search[filter_float_price:to]": str(PRICE_MAX)}
    resp = requests.get(OLX_URL, headers=HEADERS, params=params, timeout=30)
    print(f"OLX response status: {resp.status_code}, length: {len(resp.text)}", file=sys.stderr)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    listings = []
    cards = soup.select('[data-cy="l-card"]')
    print(f"Found {len(cards)} card elements", file=sys.stderr)

    for card in cards:
        link_el = card.select_one("a")
        if not link_el or not link_el.get("href"):
            continue
        url = link_el["href"]
        if url.startswith("/"):
            url = "https://www.olx.pl" + url

        listing_id = card.get("id") or url

        title_el = card.select_one("h4, h6, [data-cy='ad-card-title'] h4")
        title = title_el.get_text(strip=True) if title_el else "Без названия"

        price_el = card.select_one('[data-testid="ad-price"]')
        price = parse_price(price_el.get_text(strip=True)) if price_el else None

        location_el = card.select_one('[data-testid="location-date"]')
        location = location_el.get_text(strip=True) if location_el else ""

        if price is not None and price > PRICE_MAX:
            continue

        listings.append(
            {
                "id": listing_id,
                "title": title,
                "price": price,
                "location": location,
                "url": url,
            }
        )
    return listings


def send_telegram_message(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=15,
    )
    print(f"Telegram response status: {resp.status_code}: {resp.text}", file=sys.stderr)
    resp.raise_for_status()


def format_listing(item: dict) -> str:
    price = f"{item['price']} zł" if item["price"] is not None else "цена не указана"
    lines = [f"<b>{item['title']}</b>", price]
    if item["location"]:
        lines.append(item["location"])
    lines.append(item["url"])
    return "\n".join(lines)


def main() -> None:
    seen = load_seen()
    try:
        listings = fetch_listings()
    except requests.RequestException as exc:
        print(f"Failed to fetch OLX: {exc}", file=sys.stderr)
        sys.exit(1)

    new_listings = [item for item in listings if item["id"] not in seen]
    print(f"{len(listings)} total, {len(new_listings)} new", file=sys.stderr)

    if new_listings:
        header = f"🏠 Новые объявления на OLX (Варшава, до {PRICE_MAX} zł): {len(new_listings)}"
        send_telegram_message(header)
        for item in new_listings:
            send_telegram_message(format_listing(item))
    else:
        print("No new listings, nothing to send", file=sys.stderr)

    seen.update(item["id"] for item in listings)
    save_seen(seen)


if __name__ == "__main__":
    main()
