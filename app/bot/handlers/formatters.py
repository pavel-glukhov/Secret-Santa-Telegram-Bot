from app.bot.languages.schemes import TranslationMainSchema
from app.core.database.models import User


def get_full_name(user: User) -> str | None:
    if not user.first_name:
        return user.username

    if all([user.first_name, user.last_name]):
        return f'{user.first_name} {user.last_name}'
    else:
        return user.first_name


def user_information_formatter(
        user: User,
        lang: TranslationMainSchema) -> list:
    address = (user.get_address()
                     or lang.formatter.address_is_not_specified)
    phone_number = (user.get_number()
                    or lang.formatter.number_is_not_specified)
    timezone = (user.timezone
                or lang.formatter.timezone_is_not_specified)

    full_name = get_full_name(user)
    return [full_name, address, phone_number, timezone]


def profile_information_formatter(
        user: User,
        lang: TranslationMainSchema) -> str:
    full_name, address, number, timezone = user_information_formatter(
        user, lang)
    formatted_text = (
        f"{lang.formatter.full_name}: {full_name}\n"
        f"{lang.formatter.address}: {address}\n"
        f"{lang.formatter.number}: {number}\n"
        f"{lang.formatter.timezone}: {timezone}\n"
    )
    return formatted_text
