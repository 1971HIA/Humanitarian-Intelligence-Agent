from __future__ import annotations

from typing import Any, Dict, List
import httpx
from .config import RELIEFWEB_APPNAME

RELIEFWEB_REPORTS_URL = "https://api.reliefweb.int/v1/reports"

CRISIS_KEYWORDS = {
    "syria": "Syria humanitarian crisis funding refugees OCHA UNHCR",
    "yemen": "Yemen humanitarian crisis funding famine displacement OCHA",
    "sudan": "Sudan humanitarian crisis refugees displacement funding OCHA UNHCR",
    "gaza": "Gaza occupied Palestinian territory humanitarian crisis funding OCHA UNRWA",
    "palestine": "occupied Palestinian territory Gaza humanitarian crisis funding OCHA UNRWA",
    "lebanon": "Lebanon humanitarian crisis Syrian refugees funding UNHCR OCHA",
    "iraq": "Iraq humanitarian crisis displacement funding OCHA UNHCR",
    "afghanistan": "Afghanistan humanitarian crisis funding refugees OCHA UNHCR",
}


def expand_query(user_question: str) -> str:
    q = user_question.strip()
    lowered = q.lower()
    extra_terms = []
    for key, value in CRISIS_KEYWORDS.items():
        if key in lowered:
            extra_terms.append(value)
    if not extra_terms:
        extra_terms.append("humanitarian crisis funding refugees displacement OCHA UNHCR")
    return f"{q} {' '.join(extra_terms)}"


async def search_reports(query: str, limit: int = 6) -> List[Dict[str, Any]]:
    """Search public ReliefWeb reports and return compact source records."""
    payload = {
        "appname": RELIEFWEB_APPNAME,
        "query": {"value": expand_query(query), "operator": "AND"},
        "sort": ["date:desc"],
        "limit": limit,
        "profile": "full",
        "fields": {
            "include": [
                "title",
                "date.created",
                "source.name",
                "country.name",
                "body-html",
                "url",
                "primary_country.name",
                "disaster.name",
                "theme.name",
            ]
        },
    }
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(RELIEFWEB_REPORTS_URL, json=payload)
        res.raise_for_status()
        data = res.json()

    reports = []
    for item in data.get("data", []):
        fields = item.get("fields", {})
        body = fields.get("body-html", "") or ""
        body = body.replace("<p>", " ").replace("</p>", " ").replace("<br />", " ")
        reports.append(
            {
                "title": fields.get("title", "Untitled report"),
                "date": (fields.get("date", {}) or {}).get("created", ""),
                "source": ", ".join([s.get("name", "") for s in fields.get("source", []) if s.get("name")]),
                "country": ", ".join([c.get("name", "") for c in fields.get("country", []) if c.get("name")]),
                "url": fields.get("url", ""),
                "excerpt": body[:1200],
            }
        )
    return reports


def format_reports_for_prompt(reports: List[Dict[str, Any]]) -> str:
    if not reports:
        return "No ReliefWeb reports were found for this query."
    lines = []
    for idx, report in enumerate(reports, start=1):
        lines.append(
            f"SOURCE {idx}\n"
            f"Title: {report['title']}\n"
            f"Date: {report['date']}\n"
            f"Source organization: {report['source']}\n"
            f"Country: {report['country']}\n"
            f"URL: {report['url']}\n"
            f"Excerpt: {report['excerpt']}\n"
        )
    return "\n".join(lines)


def format_sources(reports: List[Dict[str, Any]]) -> str:
    if not reports:
        return ""
    output = ["\n\nSources searched:"]
    for idx, report in enumerate(reports[:4], start=1):
        title = report.get("title", "ReliefWeb report")[:80]
        date = report.get("date", "")[:10]
        url = report.get("url", "")
        output.append(f"{idx}. {title} ({date})\n{url}")
    return "\n".join(output)
