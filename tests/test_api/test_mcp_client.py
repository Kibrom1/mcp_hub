"""
Tests for MCP client.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_hub.api.mcp_client import MCPClient

class TestMCPClient:
    """Test MCP client functionality."""
    
    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self):
        """Test MCP client initialization."""
        client = MCPClient()
        assert client.connection_timeout == 30
        assert client.tool_timeout == 60
        assert client.active_sessions == {}
    
    @pytest.mark.asyncio
    async def test_connect_to_server_mock(self):
        """Test server connection with mocked stdio client."""
        client = MCPClient()
        
        # Mock stdio client and session
        mock_reader = Mock()
        mock_writer = Mock()
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        
        with patch('mcp_hub.api.mcp_client.stdio_client') as mock_stdio:
            mock_stdio.return_value = (mock_reader, mock_writer)
            
            with patch('mcp_hub.api.mcp_client.ClientSession') as mock_session_class:
                mock_session_class.return_value = mock_session
                
                result = await client.connect_to_server("test_command", "test_server")
                assert result == mock_session
                mock_session.initialize.assert_called_once()
