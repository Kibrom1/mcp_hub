#!/usr/bin/env python3
"""
MCP Hub - LLM Providers Support

This module provides support for multiple LLM providers including OpenAI, Anthropic, Google, and local models.
"""

import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Standardized LLM response format"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    response_time: float = 0.0

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT models provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            self.client = None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        start_time = time.time()
        
        try:
            # Remove max_tokens and temperature from kwargs to avoid duplicates
            api_kwargs = {k: v for k, v in kwargs.items() if k not in ['max_tokens', 'temperature']}
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.3),
                **api_kwargs
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def is_available(self) -> bool:
        return self.client is not None and bool(self.api_key)

class AnthropicProvider(LLMProvider):
    """Anthropic Claude models provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        super().__init__(api_key, model)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            self.client = None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Anthropic API"""
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")
        
        start_time = time.time()
        
        try:
            # Convert messages to Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.3),
                system=system_message if system_message else None,
                messages=user_messages,
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=response.content[0].text,
                model=self.model,
                provider="anthropic",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                response_time=response_time
            )
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def is_available(self) -> bool:
        return self.client is not None and bool(self.api_key)

class GoogleProvider(LLMProvider):
    """Google Gemini models provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        super().__init__(api_key, model)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model_instance = genai.GenerativeModel(model)
        except ImportError:
            self.model_instance = None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Google Gemini API"""
        if not self.model_instance:
            raise RuntimeError("Google Gemini client not initialized")
        
        start_time = time.time()
        
        try:
            import google.generativeai as genai
            
            # Convert messages to Gemini format
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get('max_tokens', 1000),
                    temperature=kwargs.get('temperature', 0.3),
                )
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider="google",
                response_time=response_time
            )
            
        except Exception as e:
            raise RuntimeError(f"Google Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        return self.model_instance is not None and bool(self.api_key)

class OllamaProvider(LLMProvider):
    """Ollama local models provider"""
    
    def __init__(self, api_key: str = "", model: str = "llama2", base_url: str = "http://localhost:11434"):
        super().__init__(api_key, model)
        self.base_url = base_url
        try:
            import requests
            self.requests = requests
        except ImportError:
            self.requests = None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Ollama API"""
        if not self.requests:
            raise RuntimeError("Requests library not available")
        
        start_time = time.time()
        
        try:
            # Convert messages to Ollama format
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
            
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get('temperature', 0.3),
                        "num_predict": kwargs.get('max_tokens', 1000),
                    }
                }
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ollama API error: {response.text}")
            
            result = response.json()
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=result["response"],
                model=self.model,
                provider="ollama",
                response_time=response_time
            )
            
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    def is_available(self) -> bool:
        if not self.requests:
            return False
        
        try:
            response = self.requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

class LLMManager:
    """Manager for multiple LLM providers"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self._load_providers()
    
    def _load_providers(self):
        """Load available LLM providers based on environment variables"""
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                self.providers["openai"] = OpenAIProvider(
                    openai_key, 
                    os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                )
                if not self.default_provider:
                    self.default_provider = "openai"
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
        
        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                self.providers["anthropic"] = AnthropicProvider(
                    anthropic_key,
                    os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
                )
                if not self.default_provider:
                    self.default_provider = "anthropic"
            except Exception as e:
                print(f"Failed to initialize Anthropic: {e}")
        
        # Google
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            try:
                self.providers["google"] = GoogleProvider(
                    google_key,
                    os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
                )
                if not self.default_provider:
                    self.default_provider = "google"
            except Exception as e:
                print(f"Failed to initialize Google: {e}")
        
        # Ollama (local)
        if os.getenv("OLLAMA_ENABLED", "false").lower() == "true":
            try:
                self.providers["ollama"] = OllamaProvider(
                    model=os.getenv("OLLAMA_MODEL", "llama2"),
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                )
                if not self.default_provider:
                    self.default_provider = "ollama"
            except Exception as e:
                print(f"Failed to initialize Ollama: {e}")
    
    def get_provider(self, provider_name: str = None) -> LLMProvider:
        """Get a specific provider or the default one"""
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]
        
        if self.default_provider and self.default_provider in self.providers:
            return self.providers[self.default_provider]
        
        raise RuntimeError("No LLM provider available")
    
    def list_available_providers(self) -> List[str]:
        """List all available providers"""
        available = []
        for name, provider in self.providers.items():
            if provider.is_available():
                available.append(name)
        return available
    
    async def generate_response(self, messages: List[Dict[str, str]], provider: str = None, **kwargs) -> LLMResponse:
        """Generate response using specified or default provider"""
        provider_instance = self.get_provider(provider)
        return await provider_instance.generate_response(messages, **kwargs)

# Global LLM manager instance
llm_manager = LLMManager()

def get_llm_manager() -> LLMManager:
    """Get the global LLM manager instance"""
    return llm_manager
