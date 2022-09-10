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
