#!/usr/bin/env python3
"""
MCP Hub - Secure Key Manager
Multiple encryption methods for API key management
"""

import os
import base64
import json
import hashlib
import secrets
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import getpass

class SecureKeyManager:
    """Advanced secure key management with multiple encryption methods"""
    
    def __init__(self, method='fernet'):
        self.method = method
        self.salt_file = '.key_salt'
        self.keys_file = '.encrypted_keys'
    
    def _get_or_create_salt(self):
        """Get existing salt or create new one"""
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            salt = secrets.token_bytes(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            os.chmod(self.salt_file, 0o600)
            return salt
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        salt = self._get_or_create_salt()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _derive_key_from_env(self) -> bytes:
        """Derive key from environment variable"""
        master_key = os.getenv('MCP_MASTER_KEY')
        if not master_key:
            raise ValueError("MCP_MASTER_KEY environment variable not set")
        
        # Use SHA256 hash of master key as encryption key
        key_hash = hashlib.sha256(master_key.encode()).digest()
        return base64.urlsafe_b64encode(key_hash)
    
    def _get_encryption_key(self, password: Optional[str] = None) -> bytes:
        """Get encryption key based on method"""
        if self.method == 'fernet':
            if password:
                return self._derive_key_from_password(password)
            else:
                return self._derive_key_from_env()
        elif self.method == 'aes':
            if password:
                return hashlib.sha256(password.encode()).digest()
            else:
                return self._derive_key_from_env()
        else:
            raise ValueError(f"Unknown encryption method: {self.method}")
    
    def encrypt_key(self, api_key: str, key_name: str, password: Optional[str] = None) -> Dict:
        """Encrypt an API key"""
        encryption_key = self._get_encryption_key(password)
        
        if self.method == 'fernet':
            cipher = Fernet(encryption_key)
            encrypted_data = cipher.encrypt(api_key.encode())
            return {
                'key_name': key_name,
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'method': 'fernet',
                'timestamp': str(int(os.path.getmtime(__file__)))
            }
        
        elif self.method == 'aes':
            # Generate random IV
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            
            # Pad the data to block size
            data = api_key.encode()
            padding_length = 16 - (len(data) % 16)
            data += bytes([padding_length] * padding_length)
            
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            return {
                'key_name': key_name,
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'iv': base64.b64encode(iv).decode(),
                'method': 'aes',
                'timestamp': str(int(os.path.getmtime(__file__)))
            }
    
    def decrypt_key(self, encrypted_info: Dict, password: Optional[str] = None) -> str:
        """Decrypt an API key"""
        encryption_key = self._get_encryption_key(password)
        
        if encrypted_info['method'] == 'fernet':
            cipher = Fernet(encryption_key)
            encrypted_data = base64.b64decode(encrypted_info['encrypted_data'])
            return cipher.decrypt(encrypted_data).decode()
        
        elif encrypted_info['method'] == 'aes':
            iv = base64.b64decode(encrypted_info['iv'])
            encrypted_data = base64.b64decode(encrypted_info['encrypted_data'])
            
            cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            padding_length = decrypted_data[-1]
            return decrypted_data[:-padding_length].decode()
    
    def save_encrypted_keys(self, keys_dict: Dict[str, str], password: Optional[str] = None):
        """Save encrypted keys to file"""
        encrypted_data = {}
        for key_name, api_key in keys_dict.items():
            encrypted_data[key_name] = self.encrypt_key(api_key, key_name, password)
        
        with open(self.keys_file, 'w') as f:
            json.dump(encrypted_data, f, indent=2)
        
        os.chmod(self.keys_file, 0o600)
        print(f"✅ Encrypted keys saved to {self.keys_file}")
    
    def load_encrypted_keys(self, password: Optional[str] = None) -> Dict[str, str]:
        """Load and decrypt keys from file"""
        try:
            with open(self.keys_file, 'r') as f:
                encrypted_data = json.load(f)
            
            decrypted_keys = {}
            for key_name, encrypted_info in encrypted_data.items():
                try:
                    decrypted_key = self.decrypt_key(encrypted_info, password)
                    decrypted_keys[key_name] = decrypted_key
                except Exception as e:
                    print(f"⚠️ Failed to decrypt {key_name}: {e}")
            
            return decrypted_keys
        except Exception as e:
            print(f"❌ Failed to load encrypted keys: {e}")
            return {}
    
    def set_environment_variables(self, keys_dict: Dict[str, str]):
        """Set environment variables from decrypted keys"""
        for key_name, api_key in keys_dict.items():
            os.environ[key_name] = api_key
        print(f"✅ Set {len(keys_dict)} environment variables")

# Convenience functions
def setup_encrypted_keys_interactive():
    """Interactive setup for encrypted API keys"""
    print("🔐 MCP Hub - Secure Key Manager")
    print("=" * 40)
    
    # Choose encryption method
    print("\n🔧 Choose encryption method:")
    print("1. Fernet (recommended)")
    print("2. AES-256")
    
    choice = input("Enter choice (1-2): ").strip()
    method = 'fernet' if choice == '1' else 'aes'
    
    # Get password
    password = getpass.getpass("Enter master password: ")
    if not password:
        print("❌ Password required")
        return
    
    # Get API keys
    keys = {}
    print("\n📝 Enter your API keys:")
    
    openai_key = getpass.getpass("OpenAI API Key (or press Enter to skip): ")
    if openai_key:
        keys['OPENAI_API_KEY'] = openai_key
    
    google_key = getpass.getpass("Google API Key (or press Enter to skip): ")
    if google_key:
        keys['GOOGLE_API_KEY'] = google_key
    
    anthropic_key = getpass.getpass("Anthropic API Key (or press Enter to skip): ")
    if anthropic_key:
        keys['ANTHROPIC_API_KEY'] = anthropic_key
    
    if not keys:
        print("❌ No API keys provided")
        return
    
    # Encrypt and save
    manager = SecureKeyManager(method=method)
    manager.save_encrypted_keys(keys, password)
    
    print("\n✅ Setup complete!")
    print(f"🔐 Keys encrypted using {method.upper()} method")
    print("💡 Use load_encrypted_keys() to decrypt them")

def load_encrypted_keys_interactive():
    """Load encrypted keys interactively"""
    print("🔓 Loading encrypted API keys...")
    
    # Try to load without password first (if using env variable)
    manager = SecureKeyManager()
    keys = manager.load_encrypted_keys()
    
    if not keys:
        # Try with password
        password = getpass.getpass("Enter master password: ")
        keys = manager.load_encrypted_keys(password)
    
    if keys:
        manager.set_environment_variables(keys)
        print(f"✅ Loaded {len(keys)} encrypted API keys")
        return True
    else:
        print("❌ Failed to load encrypted keys")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_encrypted_keys_interactive()
        elif sys.argv[1] == "load":
            load_encrypted_keys_interactive()
        else:
            print("Usage: python secure_key_manager.py [setup|load]")
    else:
        print("🔐 MCP Hub - Secure Key Manager")
        print("Usage: python secure_key_manager.py [setup|load]")
