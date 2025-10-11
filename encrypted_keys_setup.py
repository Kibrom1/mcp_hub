#!/usr/bin/env python3
"""
MCP Hub - Encrypted API Keys Setup
Provides multiple methods for secure API key management
"""

import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass

class EncryptedKeyManager:
    """Manage encrypted API keys with multiple encryption methods"""
    
    def __init__(self, master_password=None):
        self.master_password = master_password or getpass.getpass("Enter master password for encryption: ")
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self):
        """Derive encryption key from master password"""
        password = self.master_password.encode()
        salt = b'mcp_hub_salt_2024'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_key(self, api_key, key_name):
        """Encrypt an API key"""
        encrypted_key = self.cipher.encrypt(api_key.encode())
        return {
            'key_name': key_name,
            'encrypted_data': base64.b64encode(encrypted_key).decode(),
            'method': 'fernet_pbkdf2'
        }
    
    def decrypt_key(self, encrypted_data):
        """Decrypt an API key"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_key = self.cipher.decrypt(encrypted_bytes)
        return decrypted_key.decode()
    
    def save_encrypted_keys(self, keys_dict, filename='.encrypted_keys'):
        """Save encrypted keys to file"""
        encrypted_data = {}
        for key_name, api_key in keys_dict.items():
            encrypted_data[key_name] = self.encrypt_key(api_key, key_name)
        
        with open(filename, 'w') as f:
            json.dump(encrypted_data, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(filename, 0o600)
        print(f"✅ Encrypted keys saved to {filename}")
    
    def load_encrypted_keys(self, filename='.encrypted_keys'):
        """Load and decrypt keys from file"""
        try:
            with open(filename, 'r') as f:
                encrypted_data = json.load(f)
            
            decrypted_keys = {}
            for key_name, encrypted_info in encrypted_data.items():
                decrypted_key = self.decrypt_key(encrypted_info['encrypted_data'])
                decrypted_keys[key_name] = decrypted_key
            
            return decrypted_keys
        except Exception as e:
            print(f"❌ Failed to load encrypted keys: {e}")
            return {}
    
    def set_environment_variables(self, keys_dict):
        """Set environment variables from decrypted keys"""
        for key_name, api_key in keys_dict.items():
            os.environ[key_name] = api_key
        print("✅ Environment variables set from encrypted keys")

def setup_encrypted_keys():
    """Interactive setup for encrypted API keys"""
    print("🔐 MCP Hub - Encrypted API Keys Setup")
    print("=" * 50)
    
    # Get API keys from user
    keys = {}
    print("\n📝 Enter your API keys (they will be encrypted):")
    
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
        print("❌ No API keys provided. Exiting.")
        return
    
    # Encrypt and save keys
    manager = EncryptedKeyManager()
    manager.save_encrypted_keys(keys)
    
    print("\n✅ Setup complete!")
    print("🔐 Your API keys are now encrypted and stored securely")
    print("💡 Use load_encrypted_keys() to decrypt them when needed")

def load_encrypted_keys():
    """Load encrypted keys and set environment variables"""
    manager = EncryptedKeyManager()
    keys = manager.load_encrypted_keys()
    
    if keys:
        manager.set_environment_variables(keys)
        print(f"✅ Loaded {len(keys)} encrypted API keys")
        return True
    else:
        print("❌ No encrypted keys found or decryption failed")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_encrypted_keys()
    elif len(sys.argv) > 1 and sys.argv[1] == "load":
        load_encrypted_keys()
    else:
        print("Usage:")
        print("  python encrypted_keys_setup.py setup  # Setup encrypted keys")
        print("  python encrypted_keys_setup.py load    # Load encrypted keys")
