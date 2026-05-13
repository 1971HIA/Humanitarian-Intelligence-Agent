# Humanitarian Intelligence Agent (HIA)

A Telegram AI agent that answers user questions about humanitarian crises using **public ReliefWeb / UN-linked reports** and Gemini AI.

The agent is designed for the mandatory AI agent challenge: it runs automatically, is hosted online, uses public information only, and lets users ask Q&A through Telegram.

## What it does

- Receives questions from users on Telegram.
- Searches public ReliefWeb humanitarian reports in real time.
- Sends retrieved report excerpts to Gemini.
- Returns a neutral, concise answer with source links.
- Supports `/brief` for a daily-style crisis update.
- Can send a scheduled daily brief if `DAILY_CHAT_ID` is configured.

## Public data sources

- ReliefWeb API: https://api.reliefweb.int
- ReliefWeb is a humanitarian information service provided by UN OCHA and hosts public humanitarian reports.

## Free stack

- Hosting: Render free web service
- Interface: Telegram Bot API
- AI: Google Gemini API
- Data: ReliefWeb public API
- Optional database: not required for MVP

## Files

```text
app/
  main.py        FastAPI app, Telegram webhook, Q&A routes, daily brief
  reliefweb.py   ReliefWeb live search
  ai.py          Gemini answer generation + fallback
  telegram.py    Telegram sendMessage + webhook setup
  config.py      Environment variables
requirements.txt
render.yaml
.env.example
```

## Setup steps

### 1. Create Telegram bot

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot`.
3. Choose a bot name, for example: `Humanitarian Intelligence Agent`.
4. Choose a username ending in `bot`, for example: `HIA_public_bot`.
5. Copy the bot token.

### 2. Get Gemini API key

1. Go to Google AI Studio: https://aistudio.google.com/app/apikey
2. Create an API key.
3. Copy it.

### 3. Upload this project to GitHub

Your repository is:

```text
https://github.com/1971HIA/Humanitarian-Intelligence-Agent.git
```

Upload all files in this folder to that repository.

### 4. Deploy on Render

1. Go to https://render.com
2. New → Web Service
3. Connect your GitHub repository
4. Use these settings:

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Add environment variables:

```text
TELEGRAM_BOT_TOKEN=your_telegram_token
GEMINI_API_KEY=your_gemini_key
PUBLIC_BASE_URL=https://your-render-service-name.onrender.com
DAILY_BRIEF_HOUR_UTC=6
```

Optional:

```text
DAILY_CHAT_ID=your_telegram_chat_id
```

You can leave `DAILY_CHAT_ID` empty. Users can still ask questions normally.

### 5. Connect Telegram webhook

After Render deploys, open this URL in your browser:

```text
https://your-render-service-name.onrender.com/set-webhook
```

You should see something like:

```json
{"ok": true, "result": true}
```

### 6. Test the bot

Open your Telegram bot and send:

```text
/start
```

Then ask:

```text
What is the latest humanitarian situation in Yemen?
```

Try:

```text
Compare Syria and Sudan displacement.
```

Try:

```text
/brief
```

## How Q&A works

The user sends a question. The backend searches ReliefWeb public reports using the question and crisis keywords. It retrieves titles, dates, source organizations, excerpts, and URLs. Gemini then writes a neutral answer based only on the retrieved public context.

## Important public information rule

Do not upload internal reports, confidential documents, private emails, or restricted agency information. This agent is intentionally built on public ReliefWeb / UN-linked information only.

## Final challenge submission message

1️⃣ Agent Name:
Humanitarian Intelligence Agent (HIA)

2️⃣ Description:
Humanitarian Intelligence Agent (HIA) is an AI-powered humanitarian Q&A and briefing bot that searches public UN-linked humanitarian reports through ReliefWeb before answering users. It helps users ask questions about Middle East crises, humanitarian needs, displacement, donor trends, and funding gaps, then returns concise answers with public source links through Telegram.

3️⃣ Hosting Method:
Hosted on Render as a Python FastAPI service, connected to Telegram Bot API, Gemini AI API, and the public ReliefWeb API.
