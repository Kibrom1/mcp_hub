#!/usr/bin/env python3
"""
Test script for encrypted API keys
Demonstrates secure key management
"""

import os
import sys
from secure_key_manager import SecureKeyManager

def test_encryption():
    """Test the encryption system"""
    print("🔐 Testing Encrypted API Keys System")
    print("=" * 40)
    
    # Test data
    test_keys = {
        'OPENAI_API_KEY': 'sk-test123456789',
        'GOOGLE_API_KEY': 'AIza-test123456789',
        'ANTHROPIC_API_KEY': 'sk-ant-test123456789'
    }
    
    # Test password
    test_password = "test-master-password"
    
    print("\n1. Testing Fernet encryption...")
    manager = SecureKeyManager(method='fernet')
    
    # Encrypt keys
    manager.save_encrypted_keys(test_keys, test_password)
    print("✅ Keys encrypted and saved")
    
    # Load and decrypt keys
    loaded_keys = manager.load_encrypted_keys(test_password)
    print(f"✅ Loaded {len(loaded_keys)} keys")
    
    # Verify keys match
    for key_name, original_key in test_keys.items():
        if key_name in loaded_keys:
            if loaded_keys[key_name] == original_key:
                print(f"✅ {key_name}: Match")
            else:
                print(f"❌ {key_name}: Mismatch")
        else:
            print(f"❌ {key_name}: Not found")
    
    print("\n2. Testing AES encryption...")
    manager_aes = SecureKeyManager(method='aes')
    
    # Encrypt keys
    manager_aes.save_encrypted_keys(test_keys, test_password)
    print("✅ Keys encrypted with AES and saved")
    
    # Load and decrypt keys
    loaded_keys_aes = manager_aes.load_encrypted_keys(test_password)
    print(f"✅ Loaded {len(loaded_keys_aes)} keys with AES")
    
    # Verify keys match
    for key_name, original_key in test_keys.items():
        if key_name in loaded_keys_aes:
            if loaded_keys_aes[key_name] == original_key:
                print(f"✅ {key_name}: AES Match")
            else:
                print(f"❌ {key_name}: AES Mismatch")
        else:
            print(f"❌ {key_name}: AES Not found")
    
    print("\n3. Testing environment variable setting...")
    manager.set_environment_variables(loaded_keys)
    
    # Check environment variables
    for key_name in test_keys.keys():
        if os.getenv(key_name):
            print(f"✅ {key_name}: Set in environment")
        else:
            print(f"❌ {key_name}: Not set in environment")
    
    print("\n4. Testing wrong password...")
    wrong_keys = manager.load_encrypted_keys("wrong-password")
    if not wrong_keys:
        print("✅ Wrong password correctly rejected")
    else:
        print("❌ Wrong password should be rejected")
    
    print("\n🎉 All tests completed!")

def demo_usage():
    """Demonstrate usage"""
    print("\n📚 Usage Examples:")
    print("=" * 20)
    
    print("\n1. Setup encrypted keys:")
    print("   python secure_key_manager.py setup")
    
    print("\n2. Load encrypted keys:")
    print("   python secure_key_manager.py load")
    
    print("\n3. Use in your application:")
    print("   from secure_key_manager import load_encrypted_keys_interactive")
    print("   load_encrypted_keys_interactive()")
    print("   # Now API keys are available in os.environ")
    
    print("\n4. Docker usage:")
    print("   export MCP_MASTER_KEY='your-master-password'")
    print("   python docker_secure_setup.py setup")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_encryption()
    else:
        demo_usage()
