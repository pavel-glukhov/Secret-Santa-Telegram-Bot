from base64 import b64encode, b64decode
import hashlib
from typing import Union

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes


class CryptData:
    def __init__(self, key):
        self.key = key
    
    def encrypt(self, data: Union[str, int]) -> dict:
        salt = get_random_bytes(AES.block_size)
        
        private_key = hashlib.scrypt(
            self.key.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
        cipher_config = AES.new(private_key, AES.MODE_GCM)
        
        cipher_text, tag = cipher_config.encrypt_and_digest(
            bytes(data, 'utf-8'))
        return {
            'cipher_text': b64encode(cipher_text).decode('utf-8'),
            'salt': b64encode(salt).decode('utf-8'),
            'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
            'tag': b64encode(tag).decode('utf-8')
        }
    
    def decrypt(self, enc_dict: dict):
        salt = b64decode(enc_dict['salt'])
        cipher_text = b64decode(enc_dict['cipher_text'])
        nonce = b64decode(enc_dict['nonce'])
        tag = b64decode(enc_dict['tag'])
        
        private_key = hashlib.scrypt(
            self.key.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
        cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(cipher_text, tag)
        
        return decrypted
