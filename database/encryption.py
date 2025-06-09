# database/encryption.py
"""
Database field encryption using Fernet
"""
from sqlalchemy.types import TypeDecorator, String, Text
from cryptography.fernet import Fernet
from config.dev_config import SecurityConfig
import json
import logging

logger = logging.getLogger(__name__)

class EncryptedType(TypeDecorator):
    """Base class for encrypted database fields"""
    impl = Text
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fernet = Fernet(SecurityConfig.get_fernet_key())
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before storing"""
        if value is not None:
            if isinstance(value, str):
                value_bytes = value.encode('utf-8')
            else:
                value_bytes = json.dumps(value).encode('utf-8')
            
            encrypted = self.fernet.encrypt(value_bytes)
            return encrypted.decode('utf-8')
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt value after retrieving"""
        if value is not None:
            try:
                decrypted = self.fernet.decrypt(value.encode('utf-8'))
                return decrypted.decode('utf-8')
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return None
        return value

class EncryptedString(EncryptedType):
    """Encrypted string field"""
    impl = String

class EncryptedJSON(EncryptedType):
    """Encrypted JSON field"""
    
    def process_result_value(self, value, dialect):
        """Decrypt and parse JSON"""
        decrypted = super().process_result_value(value, dialect)
        if decrypted:
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted
        return decrypted