#!/usr/bin/env python3
"""Check the city's rental offers for non-residential premises (shops, offices, garages, warehouses)
and notify via Telegram when new ones appear."""
import json
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from telegram_utils import send_digest

URL = "https://mapa.um.warszawa.pl/mapaApp1/faces/oferty/ofertyWynajem.xhtml?lang=pl"
STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_commercial.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
}


def load_seen() -> set:
    if STATE_PATH.exists():
        return set(json.loads(STATE_PATH.read_text()))
    return set()


def save_seen(seen: set) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2))


def fetch_listings():
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    print(f"Response status: {resp.status_code}, length: {len(resp.text)}", file=sys.stderr)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tbody = soup.find("tbody", id="form1:dataTable1_data")
    if tbody is None:
        print("No data table found on page", file=sys.stderr)
        return []

    listings = []
    for row in tbody.find_all("tr", recursive=False):
        row_key = row.get("data-rk")
        cells = row.find_all("td", recursive=False)
        if not row_key or len(cells) < 6:
            continue

        street = cells[0].get_text(strip=True)
        forma = cells[1].get_text(strip=True)
        purposes = [li.get_text(strip=True) for li in cells[2].find_all("li")]
        area = cells[3].get_text(strip=True)
        rate = cells[4].get_text(strip=True)
        district = cells[5].get_text(strip=True)

        listings.append(
            {
                "id": row_key,
                "street": street,
                "forma": forma,
                "purposes": purposes,
                "area": area,
                "rate": rate,
                "district": district,
            }
        )
    return listings


def format_listing(item: dict) -> str:
    purposes = ", ".join(item["purposes"]) if item["purposes"] else "не указано"
    lines = [
        f"<b>{item['street']}</b>",
        f"{item['district']}",
        f"Назначение: {purposes}",
        f"Площадь: {item['area']} м², ставка: {item['rate']} zł/м²/мес нетто",
        f"Форма: {item['forma']}",
    ]
    return "\n".join(lines)


def main() -> None:
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    seen = load_seen()
    try:
        listings = fetch_listings()
    except requests.RequestException as exc:
        print(f"Failed to fetch offers: {exc}", file=sys.stderr)
        sys.exit(1)

    new_listings = [item for item in listings if item["id"] not in seen]
    print(f"{len(listings)} total, {len(new_listings)} new", file=sys.stderr)

    if dry_run:
        print("DRY_RUN=true, skipping Telegram send and state update", file=sys.stderr)
        for item in listings[:10]:
            print(format_listing(item), file=sys.stderr)
        return

    if new_listings:
        header = f"🏢 Новые нежилые помещения в аренду от города: {len(new_listings)}"
        send_digest(header, [format_listing(item) for item in new_listings])
    else:
        print("No new listings, nothing to send", file=sys.stderr)

    seen.update(item["id"] for item in listings)
    save_seen(seen)


if __name__ == "__main__":
    main()
