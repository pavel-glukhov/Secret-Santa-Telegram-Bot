from app.bot.languages import TranslationMainSchema
from app.store.database.models import User


def get_full_name(user: User) -> str | None:
    if not user.first_name:
        return user.username

    if all([user.first_name, user.last_name]):
        return f'{user.first_name} {user.last_name}'
    else:
        return user.first_name


def user_information_formatter(
        user: User,
        app_text_msg: TranslationMainSchema) -> list:
    address = (user.get_address()
                     or app_text_msg.formatter.address_is_not_specified)
    phone_number = (user.get_number()
                    or app_text_msg.formatter.number_is_not_specified)
    timezone = (user.timezone
                or app_text_msg.formatter.timezone_is_not_specified)

    full_name = get_full_name(user)
    return [full_name, address, phone_number, timezone]


def profile_information_formatter(
        user: User,
        app_text_msg: TranslationMainSchema) -> str:
    full_name, address, number, timezone = user_information_formatter(
        user, app_text_msg)
    formatted_text = (
        f"{app_text_msg.formatter.full_name}: {full_name}\n"
        f"{app_text_msg.formatter.address}: {address}\n"
        f"{app_text_msg.formatter.number}: {number}\n"
        f"{app_text_msg.formatter.timezone}: {timezone}\n"
    )
    return formatted_text
