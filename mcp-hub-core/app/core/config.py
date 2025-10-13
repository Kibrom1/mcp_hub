"""
Configuration settings for MCP Hub Core
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "MCP Hub Core API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///mcp.db"
    
    # LLM Providers
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # WebSocket
    websocket_ping_interval: int = 25
    websocket_ping_timeout: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
