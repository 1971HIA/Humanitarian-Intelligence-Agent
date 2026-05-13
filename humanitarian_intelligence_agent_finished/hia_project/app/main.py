from __future__ import annotations

from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .config import TELEGRAM_BOT_TOKEN, DAILY_CHAT_ID, DAILY_BRIEF_HOUR_UTC
from .reliefweb import search_reports, format_sources
from .ai import generate_answer
from .telegram import send_message, set_webhook

app = FastAPI(title="Humanitarian Intelligence Agent", version="1.0.0")
scheduler = AsyncIOScheduler()

WELCOME = """
🤖 Humanitarian Intelligence Agent (HIA)

Ask me about public humanitarian crises, funding gaps, displacement, refugees, UN reports, or donor trends.

Examples:
• What is the latest humanitarian situation in Yemen?
• Compare Syria and Sudan displacement.
• What are the main needs in Gaza?
• Which countries host Syrian refugees?
""".strip()


async def answer_user_question(question: str) -> str:
    reports = await search_reports(question, limit=6)
    answer = await generate_answer(question, reports)
    return answer + format_sources(reports)


@app.get("/")
async def home():
    return {
        "name": "Humanitarian Intelligence Agent",
        "status": "running",
        "description": "Telegram AI agent using public ReliefWeb/UN-linked humanitarian reports for Q&A.",
        "health": "/health",
        "ask_endpoint": "/ask?question=What is happening in Yemen?",
        "set_webhook": "/set-webhook",
    }


@app.get("/health")
async def health():
    return {"ok": True, "time_utc": datetime.now(timezone.utc).isoformat()}


@app.get("/set-webhook")
async def webhook_setup():
    return await set_webhook()


@app.get("/ask")
async def ask(question: str):
    return {"question": question, "answer": await answer_user_question(question)}


@app.post("/telegram/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    update = await request.json()
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id:
        return {"ok": True}

    if not text:
        await send_message(chat_id, "Please send a text question about a humanitarian crisis.")
        return {"ok": True}

    if text.startswith("/start"):
        await send_message(chat_id, WELCOME)
        return {"ok": True}

    if text.startswith("/brief"):
        brief = await daily_brief_text()
        await send_message(chat_id, brief)
        return {"ok": True}

    await send_message(chat_id, "Searching public humanitarian reports and preparing an answer...")
    try:
        answer = await answer_user_question(text)
    except Exception as e:
        answer = f"I could not complete the public-source search right now. Error: {type(e).__name__}. Please try again with a specific crisis name."
    await send_message(chat_id, answer)
    return {"ok": True}


async def daily_brief_text() -> str:
    topics = ["Yemen humanitarian situation", "Syria humanitarian funding refugees", "Sudan displacement crisis", "Gaza humanitarian needs"]
    sections = ["🌍 HIA Daily Humanitarian Brief\nBased on public ReliefWeb/UN-linked reports.\n"]
    for topic in topics:
        reports = await search_reports(topic, limit=3)
        answer = await generate_answer(f"Give a very short 3-bullet update on {topic}.", reports)
        sections.append(f"\n---\n{answer}")
    return "\n".join(sections)


async def send_daily_brief():
    if DAILY_CHAT_ID:
        await send_message(DAILY_CHAT_ID, await daily_brief_text())


@app.on_event("startup")
async def startup_event():
    try:
        scheduler.add_job(send_daily_brief, "cron", hour=DAILY_BRIEF_HOUR_UTC, minute=0)
        scheduler.start()
    except Exception:
        pass
