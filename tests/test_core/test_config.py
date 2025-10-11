"""
Tests for configuration management.
"""

import pytest
import tempfile
import os
from mcp_hub.core.config import Config

class TestConfig:
    """Test configuration management."""
    
    def test_config_loading(self):
        """Test configuration loading from YAML."""
        # Create temporary config file
        config_content = """
app:
  title: "Test MCP Hub"
  layout: "wide"
  debug: true

database:
  url: "sqlite:///test.db"
  echo: false

ai:
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 1000

servers:
  - name: "test_server"
    uri: "test_command"
    enabled: true

logging:
  level: "DEBUG"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "test.log"
  max_size: "1MB"
  backup_count: 3

security:
  enable_auth: false
  session_timeout: 1800
  max_requests_per_minute: 30
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_config = f.name
        
        try:
            config = Config(temp_config)
            
            # Test app config
            assert config.app.title == "Test MCP Hub"
            assert config.app.layout == "wide"
            assert config.app.debug == True
            
            # Test database config
            assert config.database.url == "sqlite:///test.db"
            assert config.database.echo == False
            
            # Test AI config
            assert config.ai.model == "gpt-4o-mini"
            assert config.ai.temperature == 0.3
            assert config.ai.max_tokens == 1000
            
        finally:
            os.unlink(temp_config)
    
    def test_get_enabled_servers(self):
        """Test getting enabled servers."""
        config = Config()
        enabled_servers = config.get_enabled_servers()
        assert all(server.enabled for server in enabled_servers)
