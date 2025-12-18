## Secret Santa Telegram Bot
[![en](https://img.shields.io/badge/lang-en-green.svg)](https://github.com/pavel-glukhov/Secret-Santa-Telegram-Bot/blob/main/README.md)
[![ru](https://img.shields.io/badge/lang-ru-yelow.svg)](https://github.com/pavel-glukhov/Secret-Santa-Telegram-Bot/blob/main/README.ru.md)

## Description
A bot for organizing a Secret Santa game via Telegram. It allows participants to easily conduct the draw, exchange wishes, and receive results. The bot also allows anonymous communication between the gift recipient and the Secret Santa.

Supports 4 languages:
- RU
- ENG
- KAZ
- UK

### Current version: 0.4.2

---
## Changelog

**v 0.4.2**
* Application startup logic reworked and separated from runtime logic.
  - Added independent runtimes for different deployment scenarios:
    - Polling runtime — for local development and testing.
    - Webhook runtime — for production with HTTPS.

**v 0.4.1**
* Ability to join a room using a URL.
* Dialogues updated.
* Application logic fixed.

**v 0.4.0**
* All ORM queries rewritten to async.
* Interface-related bugs fixed.

**v 0.3.0**
* Interactive calendar added for draw scheduling.
* Random result-sending time selection implemented.
* Various bugs fixed.

**v 0.2.2**
* Fixed message sending bugs.
* SQL queries optimized.

**v 0.2.1**
* Fixed bug with retrieving player wishes.
* Language dictionaries updated.

**v 0.2.0**
* Migration from Aiogram 2 to 3.
* SQLAlchemy replaced Tortoise ORM.
* Multi-language support added.

**v 0.1.0**
* Beta release.

---

Diagram: https://miro.com/app/board/uXjVNxWmMtE=/?share_link_id=603886678614

## Stack

- Aiogram 3
- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL
- Redis

## Features

### 1. Creating personal rooms

- Anyone can create a room for an unlimited number of people.
    - When creating, you need to specify:
        - **Room name**
        - **Budget for your group of players**
        - **Your gift wishes**

```
The USER_ROOMS_LIMIT environment variable sets the limit on the number of rooms one player can manage.
```

```
When a room is created, a random unique number is generated, its length is set by the ROOM_NUMBER_LENGTH parameter.
```

### 2. Joining an existing room by room ID

### 3. Managing your profile

- The bot allows you to enter and change the following data:
    - **First and Last Name**
    - **Home Address**
    - **Phone Number**
    - **Time Zone**
    - **Change Language**
    - **Full deletion of entered data is allowed**

```
Address and phone number are encrypted in the database using the Fernet algorithm for security.
```

### 4. Room management

- Room management menu for regular users:
    - **Leave room**
    - **Change wishes**
- Room management menu for the owner:
    - **Start game** – allows setting the distribution time
        - **Set time zone** – Set time zone for a specific region
    - **Change wishes**
    - **Settings**
        - **Delete room**
        - **Change room name**
        - **Change owner**
        - **Change room budget**

```
The room administrator cannot leave the room until management is transferred to someone else. A room can only be permanently deleted.
```

```
If there are not enough players during the draw, the room can be reactivated.
```

### 5. Communication

After the roles are drawn in the game, two options become available in rooms allowing anonymous communication between
the recipient and the sender through the bot.

- **Send message to Secret Santa**
- **Send message to recipient**

---

## Running the Bot

### Preparation
Create `.env` based on `.env.example`.

## Environment Variables

| Category | Variable | Description | Default Value | Notes |
|--------|----------|-------------|---------------|-|
| **Security** | `ENCRYPT_SECRET_KEY` | Base64-encoded 32-byte secret key used for data encryption | ❌ *none* | Required. Generate via `python manage.py generate_key` |
| **Telegram Bot** | `TELEGRAM_TOKEN` | Telegram bot token from @BotFather | ❌ *none* | Required |
|  | `TELEGRAM_LOGIN` | Bot username without `@` | ❌ *none* | Example: `my_bot_name` |
|  | `SUPPORT_ACCOUNT` | Support contact (Telegram username) | ❌ *none* | Shown on About page |
| **Room Configuration** | `ROOM_NUMBER_LENGTH` | Length of generated room ID | `6` | Allowed: `5–8` |
|  | `USER_ROOMS_LIMIT` | Maximum rooms per user | `3` ||
| **Database (PostgreSQL)** | `DATABASE_NAME` | PostgreSQL database name | ❌ *none* ||
|  | `DATABASE_USER` | Database user | ❌ *none* ||
|  | `DATABASE_PASSWORD` | Database password | ❌ *none* | ⚠️ keep secret|
|  | `DATABASE_HOST` | Database host | `db` | `db` for Docker, `localhost` for local|
|  | `DATABASE_PORT` | PostgreSQL port | `5432` ||
|  | `POOL_SIZE` | Number of persistent DB connections | `5` ||
|  | `MAX_OVERFLOW` | Max temporary connections beyond pool | `10` ||
| **Redis** | `REDIS_HOST` | Redis host | `redis` | `redis` for Docker, `localhost` for local |
|  | `REDIS_PORT` | Redis port | `6379` ||
|  | `REDIS_DB` | Redis database index | `0` ||
|  | `REDIS_PASSWORD` | Redis password | *(empty)* | If auth is disabled|
| **Webhook & SSL (Certbot)** | `DOMAIN_NAME` | Domain name for webhook (no http/https) | ❌ *none* | Required for webhook |
|  | `EMAIL` | Email for SSL certificates | ❌ *none* | Required for webhook |
|  | `CERTBOT_ENV` | Certbot environment | *(empty)* | Use `--staging` for testing|
| **System** | `SERVER_TIMEZONE` | Server timezone | `Asia/Almaty` ||



### Deployment Modes

The bot supports two independent run modes. Choose the mode depending on traffic level, infrastructure, and whether you have a public HTTPS endpoint.

---

## 🔁 Polling Mode

**Description**
- Uses Telegram long polling
- Does **not** require a public HTTPS endpoint
- Simplest setup
- Best suited for:
  - development
  - low-traffic bots
  - private servers without a domain

**Run locally**
```bash
python -m app.runtimes.polling
```

**Run with Docker**
```bash
docker-compose -f docker-compose_long_polling.yaml up
```

**Notes**
- Telegram servers actively poll your bot
- Slightly higher latency compared to webhooks
- Only one polling instance should run at a time

---

## 🌐 Webhook Mode

**Description**
- Uses Telegram webhooks
- Requires a **public HTTPS endpoint**
- Recommended for production
- Lower latency and better scalability

---

### Local Webhook Testing

You can test webhook mode locally using a tunnel (for example, `ngrok`).

```bash
uvicorn app.runtimes.webhook:create_app --reload
```

Then expose the local port and register the webhook with the generated HTTPS URL.

---

## 🚀 Production Deployment (Webhook)

### Requirements
- Public domain name
- Open ports **80** and **443**
- Valid HTTPS certificate

### Runtime Command
```bash
uvicorn app.runtimes.webhook:create_app
```

### Webhook Registration

The webhook can be registered in several ways:

**Automatically**  
The application registers the webhook on startup (recommended).

**Via management command**
```bash
python manage.py register_webhook
```

**Manually via Telegram API**
```text
https://api.telegram.org/bot{telegram_token}/setWebhook?url=https://{domain_name}/bot/
```

---

## HTTPS & Caddy

In production, the webhook is exposed **through Caddy**.

- Acts as a reverse proxy
- Automatically obtains and renews SSL certificates (Let’s Encrypt)
- Forwards HTTPS traffic to the backend container

Traffic flow:

```
Telegram → HTTPS → Caddy → backend
```

---

## 🐳 Docker Runtimes

| Runtime  | Command |
|--------|---------|
| Polling | `docker-compose -f docker-compose_long_polling.yaml up` |
| Webhook | `docker-compose up` |

---

## Docker Installation

Docker **must be installed** before running any deployment mode.

### Install Docker Engine

Follow the official installation guide for your OS:

👉 https://docs.docker.com/engine/install/

After installation, verify:
```bash
docker --version
docker compose version
```

Make sure the Docker daemon is running.

---

## Backups

### Database Backup via Docker

```bash
docker exec -t <container_name> pg_dump -U <username> <database_name> > <file_name>.sql
```

### Automated Backups

You can also use scripts located in:
```
deploy/backup
```

Recommended:
- Schedule backups via cron
- Store backups outside the VPS

---

## Access Rights Management

### Grant Superuser

```bash
python manage.py set_superuser <telegram_user_id>
```

### Remove Superuser

```bash
python manage.py remove_superuser <telegram_user_id>
```
