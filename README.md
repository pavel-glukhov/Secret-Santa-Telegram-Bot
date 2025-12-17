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

### 📂 Preparation
1. Create `.env` based on `.env.example`.
2. Generate encryption key:
```bash
python .\manage.py generate_key
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Apply migrations:
```bash
alembic upgrade head
```

### 🖥 Local Development / Testing

#### Polling Mode
- Suitable for development and small bots
- No HTTPS needed
```bash
python -m app.runtimes.polling
```
- Or with Docker:
```bash
docker-compose -f docker-compose_long_pulling.yaml up
```

#### Webhook Mode (optional local test)
- Can be tested with ngrok:
```bash
uvicorn app.runtimes.webhook:create_app --reload
```

### 🌐 Production

#### Webhook Mode
- Requires public HTTPS endpoint
```bash
uvicorn app.runtimes.webhook:create_app
```
- Webhook registers automatically, or manually:
```bash
python .\manage.py register_webhook
```
- Or via GET request:
```bash
https://api.telegram.org/bot{telegram_token}/setWebhook?url=https://{domain_name}/bot/
```

### 🔧 Docker Runtimes
| Runtime | Command |
|---------|---------|
| Polling | `docker-compose -f docker-compose_long_pulling.yaml up` |
| Webhook | `docker-compose up` |

---

## Backups
- Backup via Docker:
```bash
docker exec -t <container_name> pg_dump -U <username> <database_name> > <file_name>.sql
```
- Or use `deploy/backup` scripts.

---

## Access Rights
- Grant superuser:
```bash
python .\manage.py set_superuser <telegram_user_id>
```
- Remove superuser:
```bash
python .\manage.py remove_superuser <telegram_user_id>
```

