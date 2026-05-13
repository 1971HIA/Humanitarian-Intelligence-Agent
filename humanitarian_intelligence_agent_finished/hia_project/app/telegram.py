from __future__ import annotations

import httpx
from .config import TELEGRAM_BOT_TOKEN, PUBLIC_BASE_URL

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def split_telegram_message(text: str, max_len: int = 3900) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks, current = [], ""
    for line in text.splitlines(True):
        if len(current) + len(line) > max_len:
            chunks.append(current)
            current = line
        else:
            current += line
    if current:
        chunks.append(current)
    return chunks


async def send_message(chat_id: int | str, text: str) -> None:
    if not TELEGRAM_BOT_TOKEN:
        return
    async with httpx.AsyncClient(timeout=20) as client:
        for chunk in split_telegram_message(text):
            await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": chunk, "disable_web_page_preview": True},
            )


async def set_webhook() -> dict:
    if not TELEGRAM_BOT_TOKEN or not PUBLIC_BASE_URL:
        return {"ok": False, "description": "Missing TELEGRAM_BOT_TOKEN or PUBLIC_BASE_URL"}
    webhook_url = f"{PUBLIC_BASE_URL.rstrip('/')}/telegram/webhook/{TELEGRAM_BOT_TOKEN}"
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(f"{TELEGRAM_API}/setWebhook", json={"url": webhook_url})
        return res.json()
