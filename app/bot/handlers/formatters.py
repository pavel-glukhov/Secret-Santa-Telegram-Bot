from app.store.database.models import User


def get_full_name(user: User) -> str | None:
    if not user.first_name:
        return user.username
    
    if all([user.first_name, user.last_name]):
        return f'{user.first_name} {user.last_name}'
    else:
        return user.first_name


# TODO перенести текст
def user_information_formatter(user: User) -> list:
    address_value = user.get_address() or 'адрес не указан'
    number_value = user.get_number() or 'номер не указан'
    timezone = user.timezone or 'часовой пояс не указан'
    
    full_name = get_full_name(user)
    return [full_name, address_value, number_value, timezone]


# TODO перенести текст
def profile_information_formatter(user: User) -> str:
    full_name, address, number, timezone = user_information_formatter(user)
    formatted_text = (
        f"<b>Полное имя</b>: {full_name}\n"
        f"<b>Адрес</b>: {address}\n"
        f"<b>Номер телефона</b>: {number}\n"
        f"<b>Часовой пояс</b>: {timezone}\n"
    )
    return formatted_text
