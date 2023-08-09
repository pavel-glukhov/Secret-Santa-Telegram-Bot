from app.config import load_config
from app.store.database.models import User
from app.store.encryption import CryptData


def user_information_formatter(user: User) -> list:
    first_name = user.first_name
    last_name = user.last_name
    address = None
    number = None
    crypt = CryptData(key=load_config().encryption.key)
    
    if user.encrypted_address:
        address = crypt.decrypt(user.encrypted_address).decode('UTF8')
        
    if user.encrypted_number:
        number = crypt.decrypt(user.encrypted_number).decode('UTF8')
    
    address_value = address or 'адрес не указан'
    number_value = number or 'номер не указан'
    
    full_name = (
        f'{first_name} {last_name}'
        if any([first_name, last_name])
        else 'Имя не указано'
    )
    return [full_name, address_value, number_value]


def profile_information_formatter(user: User) -> str:
    full_name, address, number = user_information_formatter(user)
    formatted_text = (
        f"<b>Полное имя</b>: {full_name}\n"
        f"<b>Адрес</b>: {address}\n"
        f"<b>Номер телефона</b>: {number}\n"
    )
    return formatted_text
