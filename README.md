# Telegram Userbot Hosting Bot

A modular Telegram bot for connecting a user's own Telegram account and running authorized, rate-limited group-management tasks.

## Important security model

- User sessions are isolated by Telegram bot user ID.
- Stored sessions are encrypted with Fernet.
- OTPs and 2FA passwords are not stored.
- Secrets belong in environment variables.
- Session strings are never echoed or logged.
- `/tagall` does not bypass Telegram anti-spam/flood protection.
- A Telegram `FloodWait` stops the current task instead of retrying aggressively.

## Quick start

1. Create a Telegram bot with BotFather.
2. Obtain your Telegram API ID/API hash from Telegram's official developer portal.
3. Create a MongoDB database.
4. Generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

5. Copy `.env.example` to `.env` and fill the values.
6. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

7. Run:

```bash
python bot.py
```

## Session login

The included `/Logsession` flow accepts an existing Telethon `StringSession`. It encrypts the submitted session before storing it in MongoDB.

The phone-number flow is deliberately conservative: this project does not persist OTPs or 2FA passwords. If you implement full interactive phone login, keep all OTP/password values in short-lived in-memory state only and never log them.

## Tests

```bash
python -m pytest
python -m compileall .
ruff check .
```

## Railway

Use the `Procfile` worker command and configure the environment variables in Railway.

## Ubuntu VPS

Copy the repository to the server, create a virtual environment, install requirements, configure `.env`, then install the example systemd service:

```bash
sudo cp deploy/telegram-userbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-userbot
```

## Architecture

`handlers/` contains Telegram bot commands.
`services/` contains Telegram client, session, member collection, mention, rate limiting, and task management.
`database.py` manages MongoDB.
`utils/` contains security and helper functions.

This project is intended as a secure baseline and should be tested with a non-critical Telegram account before production use.
