def message_formatter(
        sender_name,
        receiver_first_name,
        receiver_last_name,
        receiver_address,
        receiver_phone,
        receiver_wish
):
    first_name = receiver_first_name
    last_name = receiver_last_name
    address = (receiver_address if receiver_address
               else ('Игрок не указал свой адрес, '
                     'свяжитесь с участником через чат '
                     'для уточнения информации'))
    number = (receiver_phone if receiver_phone
              else ('Игрок не указал свой контактный номер, '
                    'свяжитесь с участником через чат '
                    'для уточнения информации'))
    
    full_name = (
        f'{first_name} {last_name}' if all([first_name, last_name])
        else first_name
    )
    
    text = (
        '------------\n'
        f'<b>Привет {sender_name}!</b>\n'
        '<b>Поздравляю, ты стал тайным Сантой!!!!!</b> 💥💥\n\n'
        '<b>Твой получатель:</b>\n'
        f'<b>Имя:</b> {full_name}\n\n'
        f'<b>Адрес:</b> {address}\n\n'
        f'<b>Телефон:</b> {number}\n\n'
        f'<b>Пожелания к подарку:</b> {receiver_wish}\n\n'
        '<b>Скорее беги на почту и отправляй свой подарок!</b> 🏃 \n'
        '------------\n'
    )
    return text
