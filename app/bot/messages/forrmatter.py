def message_formatter(
        sender_name,
        receiver_first_name,
        receiver_last_name,
        address,
        phone, wish
):
    first_name = receiver_first_name.first_name
    last_name = receiver_last_name.last_name
    address = address or 'адрес не указан'
    number = phone or 'номер не указан'
    full_name = (
        f'{first_name} {last_name}' if any([first_name, last_name])
        else 'Имя не указано'
    )
    
    text = (
        '------------\n'
        f'<b>Привет {sender_name}!</b>\n'
        '<b>Поздравляю, ты стал тайным Сантой!!!!!</b> 💥💥\n\n'
        '<b>Твой получатель:</b>\n'
        f'<b>Имя:</b> {full_name}\n'
        f'<b>Адрес:</b> {address}\n'
        f'<b>Телефон:</b> {number}\n'
        f'<b>Комментарий:</b> {wish}\n\n'
        '<b>Скорее беги на почту и отправляй свой подарок!</b> 🏃 \n'
        '------------\n'
    )
    return text
