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

2. #### Вход в существующую комнату по ID комнаты
3. #### Управление своим профилем
   - Бот позволяет внести и изменить такие данные как:
     - **Имя и Фамилия**
     - **Домашний Адрес**
     - **Номер Телефона**
   - Разрешено полное удаление внесенных данных  
   ```Адрес и номер телефона шифруется в базе AES-256 алгоритмом в целях безопасности.```
 
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

8. ### Не реализовано в боте
   1. Требуется ревью информационных сообщений бота.
   2. Перенос всех ответов бота в БД.
   3. Покрытие тестами


9. ### Возможные планы в будущем
   3. Переписать и расширить функционал веб панели.
   4. Упаковать проект в Doker контейнеры
  
### Стек
1. Aiogram 2
2. FastAPI
3. Jinja2
4. Tortoise ORM
5. Aerich
6. PostgreSQL
7. Redis

### Запуск Бота:
 - Установить PostgreSQL и Redis, сконфигурировать и создать БД. 
 - Redis требует включения доступа по паролю:
    ```
   sudo nano /etc/redis/redis.conf
   # requirepass foobared
   ```
 - Создать свой .env файл по шаблону .env.example
 - pip install -r requirements
 - aerich migrate
 - aerich upgrade
 - python main.py


- ### Регистрация вебхука
    Используем линк в браузере
    https://api.telegram.org/bot{telegram_token}/setWebhook?url=https://{domain_name}/bot/

    Пример:
    https://api.telegram.org/bot5473814321:AAEFDZ1A5SoRsd6RFDONysEbYkl3D_VAfss/setWebhook?url=https://e87d-5-76-101-111.ngrok-free.app/bot/


- Так же, для работы **Telegram Login Widget**, требуется зарегистрировать домен вашего сайта в **@BotFather** используя команду **/setdomain**