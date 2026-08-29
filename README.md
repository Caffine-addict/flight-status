# Flight Status Tracker Bot ✈️

A serverless Telegram bot that tracks flight status, baggage claim info, and sends live updates to you and your groups. Runs entirely on GitHub Actions (free).

## Features
- **Live Updates**: Status, Departure/Arrival times, Gates, and **Baggage Claim**.
- **Multi-User**: Track flights for yourself or entire groups (e.g., "Family").
- **Interactive**: Control the bot via Telegram commands.
- **Serverless**: Runs on a schedule using GitHub Actions.

## Setup Guide

### 1. Prerequisites
- **AviationStack API Key**: [Get it here](https://aviationstack.com/) (Free).
- **Telegram Bot**: Create one via `@BotFather` and get the **Token**.

### 2. GitHub Configuration
1.  **Fork/Clone** this repository.
2.  Go to **Settings > Secrets and variables > Actions**.
3.  Add the following Repository Secrets:
    - `AVIATIONSTACK_API_KEY`
    - `TELEGRAM_BOT_TOKEN`
    - `TELEGRAM_CHAT_ID` (Your personal Chat ID, you become the "Host")
4.  Go to **Settings > Actions > General**.
5.  Under **Workflow permissions**, select **Read and write permissions** (required to save subscriptions).

### 3. Usage
**Commands:**
- `/start` - Get your Chat ID.
- `/track <flight>` - Track a flight (e.g., `/track AA100`).
- `/stop <flight>` - Stop tracking.

**Group Commands (Host Only):**
- `/addgroup <name> <chat_id>` - Add a user to a group (e.g., `/addgroup family 12345`).
- `/trackgroup <name> <flight>` - Track a flight for the whole group.

## Local Development
1.  Install dependencies: `pip install -r requirements.txt`
2.  Create a `.env` file with your keys.
3.  Run `python main.py`.
