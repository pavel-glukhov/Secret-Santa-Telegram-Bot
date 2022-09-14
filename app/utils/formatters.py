from app.database.models import User


def user_information_formatter(user: User) -> str:
    f_n = user.first_name
    l_n = user.last_name
    full_name = f'{f_n} {l_n}' if any([f_n, l_n]) else 'Имя не указано'
    address = user.address or 'адрес не указан'
    number = user.contact_number or 'номер не указан'

    formatted_text = (f"*Полное имя*: {full_name}\n"
                      f"*Адрес*: {address}\n"
                      f"*Номер телефона*: {number}\n"
                      )

    return formatted_text


def message_for_secret_santa(
        santa_name,
        receipt_name,
        receipt_address,
        receipt_number,
        receipt_wish,
) -> str:
    formatted_text = (
        '------------\n'
        f'*Привет {santa_name}!*\n'
        '*Поздравляю, ты стал тайным Сантой!!!!!* 💥💥\n\n'
        '*Твой получатель:*\n'
        f'*Имя:* {receipt_name}\n'
        f'*Адрес:* {receipt_address}\n'
        f'*Телефон:* {receipt_number}\n'
        f'*Комментарий:* {receipt_wish}\n\n'
        '*Скорее беги на почту и отправляй свой подарок!* 🏃 \n'
        '------------\n'
    )
    return formatted_text
