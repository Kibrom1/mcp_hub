"""
LLM Manager for MCP Hub Core
Handles multiple LLM providers (OpenAI, Google, Anthropic)
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
import google.generativeai as genai
import anthropic
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    response_time: float
    finish_reason: Optional[str] = None

class LLMManager:
    """Manages multiple LLM providers"""
    
    def __init__(self):
        self.providers = {}
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize available LLM providers"""
        from app.core.config import settings
        
        # OpenAI
        if settings.openai_api_key:
            try:
                openai.api_key = settings.openai_api_key
                self.providers['openai'] = {
                    'name': 'OpenAI',
                    'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                    'default_model': 'gpt-3.5-turbo'
                }
                print("✅ OpenAI provider initialized")
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
        
        # Google Gemini
        if settings.google_api_key:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.providers['google'] = {
                    'name': 'Google',
                    'models': ['models/gemini-2.5-flash', 'models/gemini-2.5-pro', 'models/gemini-pro-latest'],
                    'default_model': 'models/gemini-2.5-flash'
                }
                print("✅ Google provider initialized")
            except Exception as e:
                print(f"⚠️ Google initialization failed: {e}")
        
        # Anthropic Claude
        if settings.anthropic_api_key:
            try:
                self.providers['anthropic'] = {
                    'name': 'Anthropic',
                    'models': ['claude-3-sonnet', 'claude-3-haiku', 'claude-3-opus'],
                    'default_model': 'claude-3-sonnet'
                }
                print("✅ Anthropic provider initialized")
            except Exception as e:
                print(f"⚠️ Anthropic initialization failed: {e}")
    
    def list_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    async def generate_response_async(
        self,
        messages: List[Dict[str, str]],
        provider: str = "openai",
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> LLMResponse:
        """Generate response from specified provider"""
        start_time = datetime.now()
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        if not model:
            model = self.providers[provider]['default_model']
        
        try:
            if provider == 'openai':
                response = await self._generate_openai_response(
                    messages, model, max_tokens, temperature
                )
            elif provider == 'google':
                response = await self._generate_google_response(
                    messages, model, max_tokens, temperature
                )
            elif provider == 'anthropic':
                response = await self._generate_anthropic_response(
                    messages, model, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return LLMResponse(
                content=response['content'],
                provider=provider,
                model=model,
                tokens_used=response.get('tokens_used'),
                response_time=response_time,
                finish_reason=response.get('finish_reason')
            )
            
        except Exception as e:
            raise Exception(f"LLM generation failed: {e}")
    
    async def _generate_openai_response(self, messages, model, max_tokens, temperature):
        """Generate response using OpenAI"""
        try:
            from app.core.config import settings
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'finish_reason': response.choices[0].finish_reason
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def _generate_google_response(self, messages, model, max_tokens, temperature):
        """Generate response using Google Gemini"""
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            model_instance = genai.GenerativeModel(model)
            response = await model_instance.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            return {
                'content': response.text,
                'tokens_used': None,  # Gemini doesn't provide token count in this API
                'finish_reason': None
            }
        except Exception as e:
            raise Exception(f"Google API error: {e}")
    
    async def _generate_anthropic_response(self, messages, model, max_tokens, temperature):
        """Generate response using Anthropic Claude"""
        try:
            client = anthropic.AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            # Convert messages to Claude format
            system_message = ""
            user_messages = []
            
            for message in messages:
                if message['role'] == 'system':
                    system_message = message['content']
                else:
                    user_messages.append(message['content'])
            
            user_content = "\n".join(user_messages)
            
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=[{"role": "user", "content": user_content}]
            )
            
            return {
                'content': response.content[0].text,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens,
                'finish_reason': response.stop_reason
            }
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")
    
    def _convert_messages_to_prompt(self, messages):
        """Convert chat messages to a single prompt"""
        prompt_parts = []
        
        for message in messages:
            role = message['role']
            content = message['content']
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        return self.providers[provider]
    
    def get_all_providers_info(self) -> Dict[str, Any]:
        """Get information about all providers"""
        return self.providers

# Global instance
llm_manager = LLMManager()
