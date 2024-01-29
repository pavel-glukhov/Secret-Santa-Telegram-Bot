## Secret Santa Telegram Bot
### Описание

* Бот для игры в Тайного Санту через Telegram бота

### Реализованные Возможности

1. #### Создание персональных комнат

   - Каждый желающий может создать комнату для неограниченного количества людей.
       - При создании нужно указать:
         - **Имя комнаты**
         - **Бюджет для своей компании игроков**
         - **Свои пожелания для подарка**
         
        ```Переменная окружения USER_ROOMS_LIMIT задает лимит колличества комнат, которыми может управлять один игрок.```

       ```При создании комнаты, генерируется случайный уникальный номер, длина номеера задается параметром ROOM_NUBER_LENGTH. ```
2. #### Вход в существующую комнату по ID комнаты
3. #### Управление своим профилем
   - Бот позволяет внести и изменить такие данные как:
     - **Имя и Фамилия**
     - **Домашний Адрес**
     - **Номер Телефона**
     - **Разрешено полное удаление внесенных данных**  
   
   ```Адрес и номер телефона шифруется в базе Fernet алгоритмом в целях безопасности.```
 
4. #### Управление комнатами
   - Меню управления комнатами для обычного пользователя:       
     - **Выйти из комнаты**
     - **Изменить пожелания**
   - Меню управления комнатами для владельца:
     - **Начать игру** - позволяет установить время рассылки
     - **Изменить пожелания**
     - **Настройки**
       - **Удалить комнату** 
       - **Изменить имя комнаты**
       - **Изменить владельца**
       - **Изменить бюджет комнаты**
     
     ```Администратор комнаты не может выйти из нее, пока не передаст управление другому. Комната может быть только окончательно удалена.```
5. #### Коммуникация
    После разыгрывания ролей в игре, в комнатах доступны 2 опции, позволяющие коммуницировать анонимно между получателем и отправителем посредством бота.  
   - **Отправка сообщения Тайному Санте**
   - **Отправка сообщения получателю**  
6. ### Admin Panel 
    Реализована простая Веб Админка с простым крудом для получения информации о комнатах, играх и пользователях.
    - **Авторизация через Telegram** 
   - Позволяет просматривать:
      - Комнаты конкретного пользователя
      - Все комнаты
      - Участников комнаты
      - Всех пользователей
      - Все активные задачи на жеребьевку  
    - Реализовано:
      - Активация\деактивация пользователя
      - Удаление пользователя
      - Удаление из комнаты

7. ### Не реализовано в Web панели
   1. Настройки комнат
        - Активация\Деактивация
        - Удаление комнаты [только админ, или владелец]
        - Переименование комнаты
        - Смена времени жеребьевки
   2. Настройки профиля
        - Обновление данных
   3. не включен CSRF токен на запросах.
   4. Не реализована адаптивная верстка. 

8. ### Не реализовано в боте
   1. Перенос всех ответов бота в БД.
   2. Покрытие тестами
   3. Нужно добавить возможность указывать свой часовой пояс, что бы игрок не зависел от времени на сервере.


9. ### Возможные планы в будущем
   1. Переписать и расширить функционал веб панели.
   2. Нужно добавить certbot для добавления ssl
   3. Переписать шаблон админки с адаптивной версткой. 
  
### Стек
1. Aiogram 2
2. FastAPI
3. Jinja2
4. Tortoise ORM
5. Aerich
6. PostgreSQL
7. Redis

### Запуск Бота:
#### Ручной запуск:
 - Установить PostgreSQL и Redis, сконфигурировать и создать БД. 
   - Redis требует включения доступа по паролю:
      ```
     sudo nano /etc/redis/redis.conf
     # requirepass foobared
     ```
   - Создать свой .env файл по шаблону .env.example
   - pip install -r requirements
   - aerich init-db
   - aerich migrate
   - aerich upgrade
   - uvicorn main:create_app --reload

#### В Docker контейнере:
 - Установить Docker https://docs.docker.com/engine/install/ubuntu/
   - Создать свой .env файл по шаблону .env.example
   - sudo docker compose -f docker-compose_ssl.yaml up
   - sudo docker compose -f docker-compose.yaml up --build

    Миграции
      ```console
        docker exec -t <backend container> aerich init-db
        docker exec -t <backend container> aerich migrate
        docker exec -t <backend container> aerich upgrade
      ```
### Права доступа:
 - Что бы добавить Superuser права пользователю, выполните: 
      ```console
         python .\manage.py set_superuser <telegram_user_id>
      ```
 - Что бы удалить их, выполните **** 
      ```console
          python .\manage.py remove_superuser <telegram_user_id>
      ```
- ### Регистрация вебхука
    ```console
      python .\manage.py register_webhook
    ```
  
    Или сформируйте и сделайте GET запрос
    https://api.telegram.org/bot{telegram_token}/setWebhook?url=https://{domain_name}/bot/

    Пример:
    https://api.telegram.org/bot1234567890:AAABBBCCCDDDEEEFFF0000000_FFFFF/setWebhook?url=https://e87d-5-76-101-111.ngrok-free.app/bot/

- Так же, для работы **Telegram Login Widget**, требуется зарегистрировать домен вашего сайта в **@BotFather** используя команду **/setdomain**

### Бекапы
Бекапить базу данных можно с помощью команды ниже, добавленной в крон:  
docker exec -t <имя_контейнера> pg_dump -U <имя_пользователя> <имя_базы_данных> > <имя_файла>.sql
