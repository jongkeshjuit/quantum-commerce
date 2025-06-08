# config/vault_config.py
"""
HashiCorp Vault configuration
"""
import hvac
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class VaultClient:
    """Secure secret management with HashiCorp Vault"""
    
    def __init__(self):
        self.vault_addr = os.getenv('VAULT_ADDR', 'http://localhost:8200')
        self.vault_token = os.getenv('VAULT_TOKEN')
        
        if not self.vault_token:
            logger.warning("No Vault token provided, using development mode")
            self.client = None
        else:
            self.client = hvac.Client(
                url=self.vault_addr,
                token=self.vault_token
            )
            
            if not self.client.is_authenticated():
                raise Exception("Vault authentication failed")
            
            logger.info(f"✅ Connected to Vault at {self.vault_addr}")
    
    def get_secret(self, path: str) -> Optional[str]:
        """Get secret from Vault"""
        if not self.client:
            # Development mode - get from env
            return os.getenv(path.upper().replace('/', '_'))
        
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='secret'
            )
            return response['data']['data']['value']
        except Exception as e:
            logger.error(f"Failed to get secret {path}: {e}")
            return None
    
    def store_secret(self, path: str, value: str) -> bool:
        """Store secret in Vault"""
        if not self.client:
            logger.warning("Cannot store secrets in development mode")
            return False
        
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={'value': value},
                mount_point='secret'
            )
            logger.info(f"Stored secret at {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secret: {e}")
            return False
    
    def rotate_key(self, key_type: str) -> Dict[str, Any]:
        """Rotate cryptographic keys"""
        logger.info(f"Rotating {key_type} key")
        
        # Generate new key based on type
        if key_type == 'dilithium':
            from crypto.real_dilithium import RealDilithiumSigner
            signer = RealDilithiumSigner()
            public_key, secret_key = signer.generate_keypair()
            
            # Store in Vault
            self.store_secret(
                f'quantum-commerce/{key_type}/secret',
                secret_key.hex()
            )
            self.store_secret(
                f'quantum-commerce/{key_type}/public',
                public_key.hex()
            )
            
            return {
                'status': 'success',
                'key_type': key_type,
                'public_key': public_key.hex()[:32] + '...'
            }
        
        return {'status': 'error', 'message': 'Unknown key type'}

# Global Vault client
vault_client = VaultClient()