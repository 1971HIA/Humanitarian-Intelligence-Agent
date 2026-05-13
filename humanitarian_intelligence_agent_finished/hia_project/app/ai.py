from __future__ import annotations

import httpx
from .config import GEMINI_API_KEY, GEMINI_MODEL
from .reliefweb import format_reports_for_prompt

SYSTEM_PROMPT = """
You are Humanitarian Intelligence Agent (HIA), a neutral AI assistant for public humanitarian intelligence.
Use only public, non-confidential information. Prioritize UN-linked humanitarian sources such as ReliefWeb, OCHA, UNHCR, UNRWA, WFP, WHO, UNICEF, IOM, and official humanitarian response plans.

Rules:
1. Answer the user's question using the retrieved source excerpts when available.
2. Be neutral, factual, and professional. Avoid political propaganda or unsupported claims.
3. If exact numbers are not in the provided excerpts, say that the exact figure was not found in the retrieved sources instead of inventing it.
4. Include a short "Based on retrieved public sources" style answer.
5. Keep Telegram answers concise: 6-10 bullets or short paragraphs maximum.
6. Mention dates when important.
""".strip()


async def generate_answer(question: str, reports: list[dict]) -> str:
    context = format_reports_for_prompt(reports)
    prompt = f"""
{SYSTEM_PROMPT}

User question:
{question}

Retrieved ReliefWeb public reports:
{context}

Write the final answer now. Include a short note if the answer is limited by the retrieved reports.
""".strip()

    if not GEMINI_API_KEY:
        return fallback_answer(question, reports)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.25, "maxOutputTokens": 900},
    }
    async with httpx.AsyncClient(timeout=40) as client:
        res = await client.post(url, json=payload)
        res.raise_for_status()
        data = res.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return fallback_answer(question, reports)


def fallback_answer(question: str, reports: list[dict]) -> str:
    if not reports:
        return (
            "I searched public ReliefWeb sources but could not find enough relevant reports for this question. "
            "Try asking with a specific crisis name such as Syria, Yemen, Sudan, Gaza, Lebanon, Iraq, or Afghanistan."
        )
    bullets = ["Based on retrieved public ReliefWeb reports, I found these relevant sources:"]
    for r in reports[:5]:
        bullets.append(f"• {r.get('title','Untitled')} ({r.get('date','')[:10]}) — {r.get('source','')}")
    bullets.append("\nGemini is not configured yet, so I can retrieve sources but cannot generate a full AI summary. Add GEMINI_API_KEY in Render.")
    return "\n".join(bullets)
