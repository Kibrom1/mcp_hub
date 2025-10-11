"""
Pytest configuration and fixtures.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
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
    
    yield temp_config
    
    # Cleanup
    if os.path.exists(temp_config):
        os.unlink(temp_config)

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = Mock()
    config.app.title = "Test MCP Hub"
    config.app.layout = "wide"
    config.app.debug = True
    config.database.url = "sqlite:///test.db"
    config.database.echo = False
    config.ai.model = "gpt-4o-mini"
    config.ai.temperature = 0.3
    config.ai.max_tokens = 1000
    config.security.enable_auth = False
    config.security.session_timeout = 1800
    config.security.max_requests_per_minute = 30
    return config

@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    logger.critical = Mock()
    return logger

@pytest.fixture
def temp_database():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    yield temp_db
    
    # Cleanup
    if os.path.exists(temp_db):
        os.unlink(temp_db)
