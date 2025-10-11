"""
Tests for AI executor.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_hub.api.ai_executor import AIExecutor

class TestAIExecutor:
    """Test AI executor functionality."""
    
    def test_ai_executor_initialization(self):
        """Test AI executor initialization."""
        with patch('mcp_hub.api.ai_executor.os.getenv') as mock_getenv:
            mock_getenv.return_value = "test_api_key"
            
            executor = AIExecutor()
            assert executor.max_retries == 3
            assert executor.retry_delay == 1
    
    def test_build_prompt(self):
        """Test prompt building."""
        with patch('mcp_hub.api.ai_executor.os.getenv') as mock_getenv:
            mock_getenv.return_value = "test_api_key"
            
            executor = AIExecutor()
            
            query = "test query"
            metadata = {
                "servers": [{"name": "test_server", "uri": "test_uri"}],
                "tools": [{"server": "test_server", "name": "test_tool", "description": "Test tool"}],
                "resources": [{"server": "test_server", "name": "test_resource", "uri": "test://resource"}]
            }
            
            prompt = executor._build_prompt(query, metadata)
            assert "test query" in prompt
            assert "test_server" in prompt
            assert "test_tool" in prompt
            assert "JSON response" in prompt
