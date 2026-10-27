# Flight Status Tracker Bot

A serverless Telegram bot that tracks flights and messages you or a group when the status, gate or
baggage belt changes. It runs on a GitHub Actions schedule, so it needs no server.

## How it works

Every 5 minutes a GitHub Actions workflow runs `main.py`, which:

1. Reads new Telegram commands sent to the bot.
2. Looks up each tracked flight on the [AirLabs](https://airlabs.co/) API.
3. Compares the result with the last saved state and sends a Telegram message for anything that
   changed: status, departure and arrival times, gates, baggage claim.
4. Commits the updated subscriptions and flight states back to `data.json`.

## Commands

| Command | What it does |
|---|---|
| `/start` | Shows your chat ID |
| `/track <flight>` | Track a flight, e.g. `/track AA100` |
| `/stop <flight>` | Stop tracking it |
| `/addgroup <name> <chat_id>` | Host only: add someone to a group, e.g. `/addgroup family 12345` |
| `/trackgroup <name> <flight>` | Host only: track a flight for the whole group |

## Set it up

1. Get an [AirLabs](https://airlabs.co/) API key and create a Telegram bot with `@BotFather`.
2. Fork this repository.
3. In **Settings → Secrets and variables → Actions**, add `AIRLABS_API_KEY`,
   `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (your own chat ID; you become the host).
4. In **Settings → Actions → General → Workflow permissions**, choose **Read and write
   permissions** so the workflow can save `data.json`.

Run locally with a `.env` file holding the same three values:

```bash
pip install -r requirements.txt
python main.py
```

## Stack

Python · Telegram Bot API · AirLabs API · GitHub Actions
