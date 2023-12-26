import logging

from cryptography.exceptions import AlreadyFinalized, InternalError, InvalidKey
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class CryptData:
    def __init__(self, key):
        self.key = key
    
    def encrypt(self, data: str) -> bytes:
        try:
            fernet = Fernet(self.key)
            ciphertext = fernet.encrypt(data.encode())
            return ciphertext
        except (AlreadyFinalized, InvalidKey, InternalError) as ex:
            logger.error(
                f'encrypt error: {ex}'
            )
    
    def decrypt(self, enc_data: bytes) -> bytes:
        try:
            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(enc_data)
            return decrypted
        except (AlreadyFinalized, InvalidKey, InternalError) as ex:
            logger.error(
                f'decrypt error: {ex}'
            )
