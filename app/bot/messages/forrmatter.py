from app.bot.languages import TranslationMainSchema


def message_formatter(
        sender_name: str,
        receiver_first_name: str,
        receiver_last_name: str,
        receiver_address: str,
        receiver_phone: str,
        receiver_wish: str,
        player_language: TranslationMainSchema
) -> str:
    first_name = receiver_first_name
    last_name = receiver_last_name
    address = (receiver_address if receiver_address
               else player_language.message_formatter.address_is_not_specified)
    number = (receiver_phone if receiver_phone
              else player_language.message_formatter.number_is_not_specified)

    full_name = (
        f'{first_name} {last_name}' if all([first_name, last_name])
        else first_name
    )
    message_text = player_language.message_formatter.message_text.format(
        sender_name=sender_name,
        full_name=full_name,
        address=address,
        number=number,
        receiver_wish=receiver_wish
    )
    return message_text
