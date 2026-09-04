"""Shared Telegram helpers: batch multiple listings into as few messages as possible."""
import os
import sys
import time

import requests

TELEGRAM_MAX_LEN = 4096
# Leave headroom below Telegram's hard limit for safety.
CHUNK_LEN = 3500


def send_telegram_raw(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    print(f"Telegram response status: {resp.status_code}: {resp.text}", file=sys.stderr)
    resp.raise_for_status()


def send_digest(header: str, item_texts: list[str]) -> None:
    """Send a header plus a list of pre-formatted item blocks, packing as many
    items as fit into each message (respecting Telegram's length limit) and
    pausing briefly between messages to stay under rate limits."""
    chunks: list[str] = []
    current = header
    for item_text in item_texts:
        candidate = f"{current}\n\n{item_text}"
        if len(candidate) > CHUNK_LEN:
            chunks.append(current)
            current = item_text
        else:
            current = candidate
    chunks.append(current)

    for i, chunk in enumerate(chunks):
        send_telegram_raw(chunk)
        if i < len(chunks) - 1:
            time.sleep(1)
