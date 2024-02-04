from app.store.database.models import User


def user_information_formatter(user: User) -> list:
    first_name = user.first_name
    last_name = user.last_name
    address_value = user.get_address() or 'адрес не указан'
    number_value = user.get_number() or 'номер не указан'
    timezone = user.timezone or 'часовой пояс не указан'
    full_name = (
        f'{first_name} {last_name}' if all([first_name, last_name])
        else first_name
    )
    return [full_name, address_value, number_value, timezone]


def profile_information_formatter(user: User) -> str:
    full_name, address, number, timezone = user_information_formatter(user)
    formatted_text = (
        f"<b>Полное имя</b>: {full_name}\n"
        f"<b>Адрес</b>: {address}\n"
        f"<b>Номер телефона</b>: {number}\n"
        f"<b>Часовой пояс</b>: {timezone}\n"
    )
    return formatted_text
