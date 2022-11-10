from app.store.database.models import User


def user_information_formatter(user: User) -> list:
    f_n = user.first_name
    l_n = user.last_name
    full_name = f'{f_n} {l_n}' if any([f_n, l_n]) else 'Имя не указано'
    address = user.address or 'адрес не указан'
    number = user.contact_number or 'номер не указан'
    return [full_name, address, number]


def profile_information_formatter(user: User) -> str:
    full_name, address, number = user_information_formatter(user)
    formatted_text = (f"<b>Полное имя</b>: {full_name}\n"
                      f"<b>Адрес</b>: {address}\n"
                      f"<b>Номер телефона</b>: {number}\n"
                      )
    return formatted_text
