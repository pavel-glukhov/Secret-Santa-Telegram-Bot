from app.config import load_config
from app.store.database.models import User
from app.store.encryption import CryptData


def user_information_formatter(user: User) -> list:
    first_name = user.first_name
    last_name = user.last_name
    address = None
    number = None
    crypt = CryptData(password=load_config().encryption.password)
    
    if user.encrypted_address:
        crypt_address_data = {
            'cipher_text': user.encrypted_address,
            'salt': user.address_salt,
            'nonce': user.address_nonce,
            'tag': user.address_tag
        }
        address = crypt.decrypt(crypt_address_data).decode('UTF8')
    
    if user.encrypted_number:
        crypt_number_data = {
            'cipher_text': user.encrypted_number,
            'salt': user.number_salt,
            'nonce': user.number_nonce,
            'tag': user.number_tag
        }
        number = crypt.decrypt(crypt_number_data).decode('UTF8')
    
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
