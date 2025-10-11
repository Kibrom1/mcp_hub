#!/usr/bin/env python3
"""
MCP Hub - Docker Secure Setup
Encrypted API keys for containerized deployments
"""

import os
import base64
import json
import docker
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DockerSecureManager:
    """Secure key management for Docker deployments"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.secret_name = "mcp-api-keys"
    
    def create_docker_secret(self, keys_dict):
        """Create Docker secret with encrypted keys"""
        try:
            # Encrypt keys
            encrypted_keys = self._encrypt_keys(keys_dict)
            
            # Create Docker secret
            secret_data = json.dumps(encrypted_keys).encode()
            
            # Check if secret exists
            try:
                existing_secret = self.client.secrets.get(self.secret_name)
                existing_secret.remove()
            except docker.errors.NotFound:
                pass
            
            # Create new secret
            secret = self.client.secrets.create(
                name=self.secret_name,
                data=secret_data
            )
            
            print(f"✅ Docker secret '{self.secret_name}' created")
            return secret.id
            
        except Exception as e:
            print(f"❌ Failed to create Docker secret: {e}")
            return None
    
    def _encrypt_keys(self, keys_dict):
        """Encrypt API keys"""
        # Use environment variable as encryption key
        master_key = os.getenv('MCP_MASTER_KEY')
        if not master_key:
            raise ValueError("MCP_MASTER_KEY environment variable not set")
        
        # Derive encryption key
        salt = b'docker_mcp_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        cipher = Fernet(key)
        
        encrypted_keys = {}
        for key_name, api_key in keys_dict.items():
            encrypted_data = cipher.encrypt(api_key.encode())
            encrypted_keys[key_name] = base64.b64encode(encrypted_data).decode()
        
        return encrypted_keys
    
    def load_from_docker_secret(self):
        """Load keys from Docker secret"""
        try:
            secret = self.client.secrets.get(self.secret_name)
            secret_data = secret.attrs['Spec']['Data']
            
            # Decrypt keys
            encrypted_keys = json.loads(secret_data.decode())
            decrypted_keys = self._decrypt_keys(encrypted_keys)
            
            # Set environment variables
            for key_name, api_key in decrypted_keys.items():
                os.environ[key_name] = api_key
            
            print(f"✅ Loaded {len(decrypted_keys)} keys from Docker secret")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load from Docker secret: {e}")
            return False
    
    def _decrypt_keys(self, encrypted_keys):
        """Decrypt API keys"""
        master_key = os.getenv('MCP_MASTER_KEY')
        if not master_key:
            raise ValueError("MCP_MASTER_KEY environment variable not set")
        
        # Derive decryption key
        salt = b'docker_mcp_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        cipher = Fernet(key)
        
        decrypted_keys = {}
        for key_name, encrypted_data in encrypted_keys.items():
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_key = cipher.decrypt(encrypted_bytes)
            decrypted_keys[key_name] = decrypted_key.decode()
        
        return decrypted_keys

def setup_docker_secrets():
    """Setup Docker secrets for API keys"""
    print("🐳 MCP Hub - Docker Secure Setup")
    print("=" * 40)
    
    # Check if MCP_MASTER_KEY is set
    if not os.getenv('MCP_MASTER_KEY'):
        print("❌ MCP_MASTER_KEY environment variable not set")
        print("💡 Set it with: export MCP_MASTER_KEY='your-master-password'")
        return
    
    # Get API keys
    keys = {}
    print("\n📝 Enter your API keys:")
    
    openai_key = input("OpenAI API Key (or press Enter to skip): ").strip()
    if openai_key:
        keys['OPENAI_API_KEY'] = openai_key
    
    google_key = input("Google API Key (or press Enter to skip): ").strip()
    if google_key:
        keys['GOOGLE_API_KEY'] = google_key
    
    anthropic_key = input("Anthropic API Key (or press Enter to skip): ").strip()
    if anthropic_key:
        keys['ANTHROPIC_API_KEY'] = anthropic_key
    
    if not keys:
        print("❌ No API keys provided")
        return
    
    # Create Docker secret
    manager = DockerSecureManager()
    secret_id = manager.create_docker_secret(keys)
    
    if secret_id:
        print("\n✅ Docker secret created successfully!")
        print("🐳 Use the following in your docker-compose.yml:")
        print(f"""
secrets:
  api-keys:
    external: true
    name: {manager.secret_name}

services:
  mcp-hub:
    secrets:
      - api-keys
    environment:
      - MCP_MASTER_KEY=${{MCP_MASTER_KEY}}
""")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_docker_secrets()
    else:
        print("🐳 MCP Hub - Docker Secure Setup")
        print("Usage: python docker_secure_setup.py setup")
