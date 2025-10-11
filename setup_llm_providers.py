#!/usr/bin/env python3
"""
MCP Hub - LLM Providers Setup Script

This script helps configure multiple LLM providers for the MCP Hub.
"""

import os
import sys
import subprocess
from typing import List, Dict

def check_environment():
    """Check current environment and available providers"""
    print("🔍 Checking LLM Provider Environment")
    print("=" * 50)
    
    providers = {
        "OpenAI": {
            "key": "OPENAI_API_KEY",
            "package": "openai",
            "status": "❌ Not configured"
        },
        "Anthropic": {
            "key": "ANTHROPIC_API_KEY", 
            "package": "anthropic",
            "status": "❌ Not configured"
        },
        "Google": {
            "key": "GOOGLE_API_KEY",
            "package": "google-generativeai",
            "status": "❌ Not configured"
        },
        "Ollama": {
            "key": "OLLAMA_ENABLED",
            "package": "requests",
            "status": "❌ Not configured"
        }
    }
    
    # Check API keys
    for provider, config in providers.items():
        if os.getenv(config["key"]):
            config["status"] = "✅ API Key configured"
        else:
            config["status"] = f"❌ Missing {config['key']}"
    
    # Check packages
    for provider, config in providers.items():
        try:
            __import__(config["package"])
            config["package_status"] = "✅ Installed"
        except ImportError:
            config["package_status"] = "❌ Not installed"
    
    # Display status
    for provider, config in providers.items():
        print(f"\n🤖 {provider}:")
        print(f"   API Key: {config['status']}")
        print(f"   Package: {config['package_status']}")
    
    return providers

def install_packages():
    """Install required packages for LLM providers"""
    print("\n📦 Installing LLM Provider Packages")
    print("=" * 40)
    
    packages = [
        "openai",
        "anthropic", 
        "google-generativeai",
        "requests"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def setup_environment_file():
    """Create environment file template"""
    env_content = """# MCP Hub - LLM Providers Environment Configuration

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Anthropic Configuration  
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Google Gemini Configuration
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL=gemini-pro

# Ollama Local Configuration
OLLAMA_ENABLED=false
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434

# Default provider (auto-selected based on available keys)
DEFAULT_LLM_PROVIDER=openai
"""
    
    with open(".env.llm", "w") as f:
        f.write(env_content)
    
    print("\n📝 Created .env.llm template file")
    print("   Edit this file with your API keys")

def show_setup_instructions():
    """Show setup instructions for each provider"""
    print("\n📋 LLM Provider Setup Instructions")
    print("=" * 40)
    
    instructions = {
        "OpenAI": {
            "steps": [
                "1. Get API key from: https://platform.openai.com/api-keys",
                "2. Set environment variable: export OPENAI_API_KEY='your-key'",
                "3. Add to .env.llm: OPENAI_API_KEY=your-key"
            ]
        },
        "Anthropic": {
            "steps": [
                "1. Get API key from: https://console.anthropic.com/",
                "2. Set environment variable: export ANTHROPIC_API_KEY='your-key'",
                "3. Add to .env.llm: ANTHROPIC_API_KEY=your-key"
            ]
        },
        "Google": {
            "steps": [
                "1. Get API key from: https://makersuite.google.com/app/apikey",
                "2. Set environment variable: export GOOGLE_API_KEY='your-key'",
                "3. Add to .env.llm: GOOGLE_API_KEY=your-key"
            ]
        },
        "Ollama": {
            "steps": [
                "1. Install Ollama: https://ollama.ai/",
                "2. Pull a model: ollama pull llama2",
                "3. Set environment: export OLLAMA_ENABLED=true",
                "4. Add to .env.llm: OLLAMA_ENABLED=true"
            ]
        }
    }
    
    for provider, config in instructions.items():
        print(f"\n🤖 {provider} Setup:")
        for step in config["steps"]:
            print(f"   {step}")

def test_providers():
    """Test configured providers"""
    print("\n🧪 Testing LLM Providers")
    print("=" * 30)
    
    try:
        from llm_providers import get_llm_manager
        
        llm_manager = get_llm_manager()
        available = llm_manager.list_available_providers()
        
        if available:
            print(f"✅ Available providers: {', '.join(available)}")
            
            for provider_name in available:
                try:
                    provider = llm_manager.get_provider(provider_name)
                    if provider.is_available():
                        print(f"   ✅ {provider_name}: Ready")
                    else:
                        print(f"   ❌ {provider_name}: Not available")
                except Exception as e:
                    print(f"   ❌ {provider_name}: Error - {e}")
        else:
            print("❌ No providers available")
            print("   Configure API keys and restart the application")
            
    except Exception as e:
        print(f"❌ Error testing providers: {e}")

def main():
    """Main setup function"""
    print("🚀 MCP Hub - Multi-LLM Setup")
    print("=" * 40)
    
    # Check current environment
    providers = check_environment()
    
    # Install packages
    install_packages()
    
    # Create environment file
    setup_environment_file()
    
    # Show setup instructions
    show_setup_instructions()
    
    # Test providers
    test_providers()
    
    print("\n🎉 Setup Complete!")
    print("\n📝 Next Steps:")
    print("1. Configure your API keys in .env.llm")
    print("2. Source the environment: source .env.llm")
    print("3. Run the multi-LLM app: streamlit run app_multi_llm.py")
    print("\n🔧 Available Commands:")
    print("   python setup_llm_providers.py --test    # Test providers")
    print("   python setup_llm_providers.py --check   # Check status")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_providers()
        elif sys.argv[1] == "--check":
            check_environment()
        else:
            print("Usage: python setup_llm_providers.py [--test|--check]")
    else:
        main()
