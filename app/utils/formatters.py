from app.database.models import User


async def user_information_formatter(user: User) -> str:
    first_name = user.first_name or ''
    last_name = user.last_name or ''
    address = user.address or 'адрес не указан'
    number = user.contact_number or 'номер не указан'
    email = user.email or 'email не указан'

    formatted_text = (f"*Полное имя*: {first_name} {last_name}\n"
                      f"*Адрес*: {address}\n"
                      f"*Номер телефона*: {number}\n"
                      f"*Email*: {email}")

    return formatted_text
