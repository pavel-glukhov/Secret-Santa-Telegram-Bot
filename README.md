## Secret Santa Telegram Bot 
[![en](https://img.shields.io/badge/lang-en-green.svg)](https://github.com/pavel-glukhov/Secret-Santa-Telegram-Bot/blob/main/README.md)
[![ru](https://img.shields.io/badge/lang-ru-yelow.svg)](https://github.com/pavel-glukhov/Secret-Santa-Telegram-Bot/blob/main/README.ru.md)

## Description
A bot for organizing a Secret Santa game via Telegram. It allows participants to easily conduct the draw,
exchange wishes, and receive results. The bot also allows anonymous communication between the gift recipient and the Secret Santa.

Supports 4 languages, translated using machine translation.
Included languages:

1. RU
2. ENG
3. KAZ
4. UK

### Current version: 0.4.1

---
## Changelog

**v 0.4.1**
* Added the ability to join a room using a URL.
* Dialogues updated.
* Application logic fixed.

**v 0.4**
* All ORM queries were rewritten to async.
* Some interface-related bugs fixed.

**v 0.3**
* Removed the old method of specifying the draw date.
* Added an interactive calendar and random result-sending time selection within time periods.
* Some bugs and issues fixed.

**v 0.2.2**
* Fixed some bugs related to message sending.
* Some SQL queries optimized.

**v 0.2.1**
* Fixed a bug with retrieving player wishes in the room.
* Updated language dictionaries.

**v 0.2**
* The application was rewritten from Aiogram 2 to version 3.
* SQL queries migrated from Tortoise ORM to SQLAlchemy.
* Added support for other languages.
* Various bugs fixed.

**v 0.1**
* Beta version of the bot released.

---

Diagram: https://miro.com/app/board/uXjVNxWmMtE=/?share_link_id=603886678614

### Stack

1. Aiogram 3
2. FastAPI
3. SQLAlchemy 2
4. Alembic
5. PostgreSQL
6. Redis

1. #### Creating personal rooms

    - Anyone can create a room for an unlimited number of people.
        - When creating, you need to specify:
            - **Room name**
            - **Budget for your group of players**
            - **Your gift wishes**

      ```The USER_ROOMS_LIMIT environment variable sets the limit on the number of rooms one player can manage.```

      ```When a room is created, a random unique number is generated, its length is set by the ROOM_NUMBER_LENGTH parameter. ```
2. #### Joining an existing room by room ID
3. #### Managing your profile
    - The bot allows you to enter and change the following data:
        - **First and Last Name**
        - **Home Address**
        - **Phone Number**
        - **Time Zone**
        - **Full deletion of entered data is allowed**

   ```Address and phone number are encrypted in the database using the Fernet algorithm for security.```

4. #### Room management
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

      ```The room administrator cannot leave the room until management is transferred to someone else. A room can only be permanently deleted.```

      ```If there are not enough players during the draw, the room can be reactivated.```
5. #### Communication
   After the roles are drawn in the game, two options become available in rooms allowing anonymous communication between
   the recipient and the sender through the bot.
    - **Send message to Secret Santa**
    - **Send message to recipient**

### Running the Bot:
- Create your own .env file based on the .env.example template
- To generate the **ENCRYPT_SECRET_KEY** parameter in the **.env** file, use:
     ```
        python .\manage.py generate_key
    ```

#### Manual launch:

- Install PostgreSQL and Redis, configure them, and create the database.
    - Redis requires enabling password access:
       ```
      sudo nano /etc/redis/redis.conf
      # requirepass foobared

    -  ```pip install -r requirements.txt ```
    -  ```alembic upgrade head ```
    -  ```uvicorn app.core.cli:create_app ```
    

#### In Docker container:

- Install Docker https://docs.docker.com/engine/install/ubuntu/
    - Create your own .env file based on the .env.example template
  
- Run Docker Compose
    -  ```docker-compose up -d ```
- Rebuild after code updates
    -  ```docker-compose build ```
- Restart containers with rebuilt images:
    -  ```docker-compose up -d --build ```


  Migrations
     ```console
       docker exec -t <backend container> alembic upgrade head
     ```

### Access rights:

- To grant Superuser rights to a user, run:
     ```console
        python .\manage.py set_superuser <telegram_user_id>
     ```
- To remove them, run:
     ```console
         python .\manage.py remove_superuser <telegram_user_id>
     ```
- ### Webhook registration
    ```console
      python .\manage.py register_webhook
    ```

  Or create and make a GET request
   ```https://api.telegram.org/bot{telegram_token}/setWebhook?url=https://{domain_name}/bot/ ```

  Example:
   ```https://api.telegram.org/bot1234567890:AAABBBCCCDDDEEEFFF0000000_FFFFF/setWebhook?url=https://e87d-5-76-101-111.ngrok-free.app/bot/ ```

### Backups

The database can be backed up using the command below, added to cron:
``docker exec -t <container_name> pg_dump -U <username> <database_name> > <file_name>.sql
``

```Or add the ready-made script from deploy\backup to cron. You will need to adjust the settings for yourself. ```