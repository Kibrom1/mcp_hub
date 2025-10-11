import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import modules to test
from config import Config, AppConfig, DatabaseConfig, AIConfig, ServerConfig, LoggingConfig, SecurityConfig
from db import DatabaseManager, MCPServer, MCPTool, MCPResource
from logger import MCPHubLogger
from auth import AuthManager
from error_handler import ErrorHandler
from mcp_multi_client import MCPClient
from auto_execute import AIExecutor

class TestConfig:
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test configuration loading from YAML"""
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
            
            # Test servers
            assert len(config.servers) == 1
            assert config.servers[0].name == "test_server"
            assert config.servers[0].uri == "test_command"
            assert config.servers[0].enabled == True
            
            # Test logging config
            assert config.logging.level == "DEBUG"
            assert config.logging.max_size == "1MB"
            assert config.logging.backup_count == 3
            
            # Test security config
            assert config.security.enable_auth == False
            assert config.security.session_timeout == 1800
            assert config.security.max_requests_per_minute == 30
            
        finally:
            os.unlink(temp_config)
    
    def test_get_enabled_servers(self):
        """Test getting enabled servers"""
        config = Config()
        enabled_servers = config.get_enabled_servers()
        assert all(server.enabled for server in enabled_servers)
    
    def test_get_server_by_name(self):
        """Test getting server by name"""
        config = Config()
        server = config.get_server_by_name("filesystem")
        assert server.name == "filesystem"
        
        with pytest.raises(ValueError):
            config.get_server_by_name("nonexistent")

class TestDatabase:
    """Test database functionality"""
    
    def test_database_manager_initialization(self):
        """Test database manager initialization"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name
        
        try:
            # Mock config for testing
            with patch('db.config') as mock_config:
                mock_config.database.url = f"sqlite:///{temp_db}"
                mock_config.database.echo = False
                
                db_manager = DatabaseManager()
                assert db_manager.engine is not None
                assert db_manager.SessionLocal is not None
                
        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)
    
    def test_database_models(self):
        """Test database model creation"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name
        
        try:
            with patch('db.config') as mock_config:
                mock_config.database.url = f"sqlite:///{temp_db}"
                mock_config.database.echo = False
                
                db_manager = DatabaseManager()
                session = db_manager.get_session()
                
                # Test MCPServer model
                server = MCPServer(
                    name="test_server",
                    uri="test_uri",
                    enabled=True
                )
                session.add(server)
                session.commit()
                
                # Test MCPTool model
                tool = MCPTool(
                    id="test_tool_1",
                    server_name="test_server",
                    name="test_tool",
                    description="Test tool description",
                    parameters='{"param1": "string"}'
                )
                session.add(tool)
                session.commit()
                
                # Test MCPResource model
                resource = MCPResource(
                    id="test_resource_1",
                    server_name="test_server",
                    name="test_resource",
                    uri="test://resource"
                )
                session.add(resource)
                session.commit()
                
                # Verify data was saved
                assert session.query(MCPServer).count() == 1
                assert session.query(MCPTool).count() == 1
                assert session.query(MCPResource).count() == 1
                
                session.close()
                
        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)

class TestLogger:
    """Test logging functionality"""
    
    def test_logger_initialization(self):
        """Test logger initialization"""
        with patch('logger.config') as mock_config:
            mock_config.logging.level = "INFO"
            mock_config.logging.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            mock_config.logging.file = None
            mock_config.logging.max_size = "10MB"
            mock_config.logging.backup_count = 5
            
            logger = MCPHubLogger()
            assert logger.logger is not None
            assert logger.logger.level == 20  # INFO level
    
    def test_logging_methods(self):
        """Test logging methods"""
        with patch('logger.config') as mock_config:
            mock_config.logging.level = "DEBUG"
            mock_config.logging.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            mock_config.logging.file = None
            mock_config.logging.max_size = "10MB"
            mock_config.logging.backup_count = 5
            
            logger = MCPHubLogger()
            
            # Test different log levels
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            logger.debug("Test debug message")
            logger.critical("Test critical message")
            
            # Test specialized logging methods
            logger.log_tool_execution("test_server", "test_tool", {"arg1": "value1"}, "result", 1.5)
            logger.log_ai_query("test query", "test response", 2.0)

class TestAuth:
    """Test authentication functionality"""
    
    def test_auth_manager_initialization(self):
        """Test auth manager initialization"""
        with patch('auth.config') as mock_config:
            mock_config.security.enable_auth = False
            mock_config.security.session_timeout = 3600
            mock_config.security.max_requests_per_minute = 60
            
            auth_manager = AuthManager()
            assert auth_manager.session_timeout == 3600
            assert auth_manager.max_requests == 60
    
    def test_password_hashing(self):
        """Test password hashing"""
        with patch('auth.config') as mock_config:
            mock_config.security.enable_auth = False
            mock_config.security.session_timeout = 3600
            mock_config.security.max_requests_per_minute = 60
            
            auth_manager = AuthManager()
            
            # Test password hashing
            password = "test_password"
            hashed = auth_manager._hash_password(password)
            assert hashed != password
            assert len(hashed) == 64  # SHA-256 hash length
            assert hashed == auth_manager._hash_password(password)  # Consistent hashing
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        with patch('auth.config') as mock_config:
            mock_config.security.enable_auth = False
            mock_config.security.session_timeout = 3600
            mock_config.security.max_requests_per_minute = 2  # Low limit for testing
            
            auth_manager = AuthManager()
            
            # Mock session state
            with patch('auth.st.session_state') as mock_session:
                mock_session.get.return_value = "test_user"
                
                # Test rate limiting
                assert auth_manager.check_rate_limit() == True
                assert auth_manager.check_rate_limit() == True
                assert auth_manager.check_rate_limit() == False  # Should be rate limited

class TestErrorHandler:
    """Test error handling functionality"""
    
    def test_error_handler_initialization(self):
        """Test error handler initialization"""
        error_handler = ErrorHandler()
        assert error_handler.error_count == 0
        assert error_handler.max_errors == 10
    
    def test_error_handling(self):
        """Test error handling"""
        error_handler = ErrorHandler()
        
        # Test error handling
        test_error = ValueError("Test error")
        result = error_handler.handle_error(test_error, "test context", show_to_user=False)
        
        assert result["error"] == True
        assert result["error_type"] == "ValueError"
        assert result["message"] == "Test error"
        assert result["context"] == "test context"
        assert error_handler.error_count == 1
    
    def test_input_validation(self):
        """Test input validation"""
        error_handler = ErrorHandler()
        
        # Test valid input
        valid_data = {"field1": "value1", "field2": "value2"}
        assert error_handler.validate_input(valid_data, ["field1", "field2"], "test input") == True
        
        # Test invalid input
        invalid_data = {"field1": "value1"}
        assert error_handler.validate_input(invalid_data, ["field1", "field2"], "test input") == False
        
        # Test empty input
        assert error_handler.validate_input(None, [], "test input") == False

class TestMCPClient:
    """Test MCP client functionality"""
    
    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self):
        """Test MCP client initialization"""
        client = MCPClient()
        assert client.connection_timeout == 30
        assert client.tool_timeout == 60
        assert client.active_sessions == {}
    
    @pytest.mark.asyncio
    async def test_connect_to_server_mock(self):
        """Test server connection with mocked stdio client"""
        client = MCPClient()
        
        # Mock stdio client and session
        mock_reader = Mock()
        mock_writer = Mock()
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        
        with patch('mcp_multi_client.stdio_client') as mock_stdio:
            mock_stdio.return_value = (mock_reader, mock_writer)
            
            with patch('mcp_multi_client.ClientSession') as mock_session_class:
                mock_session_class.return_value = mock_session
                
                result = await client.connect_to_server("test_command", "test_server")
                assert result == mock_session
                mock_session.initialize.assert_called_once()

class TestAIExecutor:
    """Test AI executor functionality"""
    
    def test_ai_executor_initialization(self):
        """Test AI executor initialization"""
        with patch('auto_execute.os.getenv') as mock_getenv:
            mock_getenv.return_value = "test_api_key"
            
            executor = AIExecutor()
            assert executor.max_retries == 3
            assert executor.retry_delay == 1
    
    def test_build_prompt(self):
        """Test prompt building"""
        with patch('auto_execute.os.getenv') as mock_getenv:
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

# Integration tests
class TestIntegration:
    """Test integration between components"""
    
    def test_config_database_integration(self):
        """Test configuration and database integration"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name
        
        try:
            with patch('db.config') as mock_config:
                mock_config.database.url = f"sqlite:///{temp_db}"
                mock_config.database.echo = False
                
                # Test that database manager uses config
                db_manager = DatabaseManager()
                assert db_manager.engine.url.database == temp_db
                
        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)
    
    def test_logger_error_handler_integration(self):
        """Test logger and error handler integration"""
        with patch('logger.config') as mock_logger_config:
            mock_logger_config.logging.level = "INFO"
            mock_logger_config.logging.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            mock_logger_config.logging.file = None
            mock_logger_config.logging.max_size = "10MB"
            mock_logger_config.logging.backup_count = 5
            
            logger = MCPHubLogger()
            error_handler = ErrorHandler()
            
            # Test that error handler uses logger
            test_error = RuntimeError("Test runtime error")
            result = error_handler.handle_error(test_error, "integration test", show_to_user=False)
            
            assert result["error"] == True
            assert result["error_type"] == "RuntimeError"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
